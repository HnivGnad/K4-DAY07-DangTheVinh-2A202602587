"""Shopee retrieval benchmark; no LLM generation or automatic grading."""
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import re
import time
from src.chunking import FixedSizeChunker, RecursiveChunker, SentenceChunker
from src.embeddings import GeminiEmbedder, LocalEmbedder, MockEmbedder
from src.heading_chunking import HeadingChunker
from src.models import Document
from src.store import EmbeddingStore

ROOT = Path(__file__).resolve().parent
QUESTIONS = [
    'Người mua cần thực hiện những bước nào trên ứng dụng Shopee để gửi yêu cầu Trả hàng/Hoàn tiền?',
    'Khi Shopee yêu cầu bổ sung bằng chứng cho yêu cầu Trả hàng/Hoàn tiền, Người mua có bao nhiêu thời gian để phản hồi?',
    'Những nhóm sản phẩm nào thuộc danh mục hạn chế không được trả hàng hoặc không áp dụng lý do "Đổi ý/không còn nhu cầu"?',
    'Shopee Xu và Mã giảm giá (Voucher) đã sử dụng sẽ được hoàn lại như thế nào khi yêu cầu Trả hàng/Hoàn tiền thành công?',
    'Người bán vi phạm quy định đăng bán sản phẩm trên Shopee (như bán hàng cấm, hàng giả, gian lận) sẽ bị xử lý bằng những hình thức nào?',
]


class CachedEmbedder:
    """Persist successful vectors and pace Gemini requests across this run."""

    def __init__(self, embedder, provider, cache_dir, interval=1.0):
        self.embedder = embedder
        self.provider = provider
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.interval = interval if provider == 'gemini' else 0
        self.last_request = None
        self.namespace = f'{provider}:{embedder._backend_name}:normalized-v1'

    def __call__(self, text):
        key = hashlib.sha256((self.namespace + '\0' + text).encode('utf-8')).hexdigest()
        path = self.cache_dir / f'{key}.json'
        if path.exists():
            return json.loads(path.read_text(encoding='utf-8'))
        for attempt in range(6):
            if self.last_request is not None:
                time.sleep(max(0, self.interval - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            try:
                vector = self.embedder(text)
                break
            except Exception as error:
                message = str(error)
                if self.provider != 'gemini' or str(getattr(error, 'code', '')) != '429':
                    raise
                if attempt == 5 or 'PerDay' in message or 'limit: 0,' in message:
                    raise RuntimeError(
                        'Gemini quota unavailable. Successful embeddings are cached; '
                        'check AI Studio limits and rerun later.'
                    ) from error
                match = re.search(r'retry in ([\d.]+)s', message, re.I)
                delay = max(15 * (attempt + 1), float(match.group(1)) + 1 if match else 0)
                print(f'Gemini 429: waiting {delay:.1f}s, retry {attempt + 1}/5...', flush=True)
                time.sleep(delay)
        norm = math.sqrt(sum(v*v for v in vector)) or 1.0
        normalized = [v/norm for v in vector]
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(normalized), encoding='utf-8')
        temporary.replace(path)
        return normalized


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider', choices=['mock', 'gemini', 'local'], default='mock')
    parser.add_argument('--strategy', choices=['heading', 'fixed', 'sentence', 'recursive'], default='heading')
    parser.add_argument('--chunk-size', type=int, default=1000)
    parser.add_argument('--output', default='ket_qua_benchmark.txt')
    parser.add_argument('--request-interval', type=float, default=1.0,
                        help='Minimum seconds between Gemini requests (default: 1)')
    args = parser.parse_args()
    if args.chunk_size <= 50:
        parser.error('--chunk-size must exceed 50')
    if not math.isfinite(args.request_interval) or args.request_interval < 0:
        parser.error('--request-interval must be finite and nonnegative')
    chunker = {
        'heading': HeadingChunker(args.chunk_size),
        'fixed': FixedSizeChunker(args.chunk_size, 50),
        'sentence': SentenceChunker(3),
        'recursive': RecursiveChunker(chunk_size=args.chunk_size),
    }[args.strategy]
    corpus = ROOT / 'data/shopee'
    with (corpus / 'sources.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    documents = []
    for row in rows:
        path = (corpus / row['file_name']).resolve()
        if path.parent != corpus.resolve() or path.suffix != '.md':
            raise ValueError('Invalid corpus path')
        text = path.read_text(encoding='utf-8-sig')
        match = re.match(r'\A---\s*\n.*?\n---\s*(?:\n|$)', text, re.S)
        if not match:
            raise ValueError(f'Missing frontmatter: {path.name}')
        body = text[match.end():].strip()
        # The manifest is the metadata source; review notes are excluded.
        meta = {k: row[k] for k in ['doc_id', 'title', 'source_url', 'retrieved_at', 'document_version', 'audience', 'category', 'language']}
        for index, chunk in enumerate(chunker.chunk(body)):
            documents.append(Document(id=f"{row['doc_id']}#{index}", content=chunk, metadata={**meta, 'chunk_index': index}))
    if args.provider == 'gemini':
        from dotenv import load_dotenv
        load_dotenv(ROOT / '.env')
        embedder = GeminiEmbedder(os.getenv('GEMINI_EMBEDDING_MODEL', 'gemini-embedding-001'))
    elif args.provider == 'local':
        embedder = LocalEmbedder()
    else:
        embedder = MockEmbedder()
    embed = CachedEmbedder(embedder, args.provider, ROOT / '.embedding-cache',
                           args.request_interval)
    print(f'Embedding {len(documents)} chunks using {args.provider}...', flush=True)
    store = EmbeddingStore(embedding_fn=embed)
    for index, document in enumerate(documents, 1):
        store.add_documents([document])
        if index % 10 == 0 or index == len(documents):
            print(f'Loaded {index}/{len(documents)} chunks (saved in cache).', flush=True)
    lines = [
        f'Strategy: {args.strategy}; chunk_size: {args.chunk_size}; fixed overlap: 50; sentence limit: 3',
        f'Backend: {embedder._backend_name}',
        f'Documents: {len(rows)}; chunks: {store.get_collection_size()}',
        'Retrieval only: chưa sinh câu trả lời LLM, chưa chấm điểm.',
        'Câu 2, 4, 5 còn thiếu nguồn; câu 3 cần đối chiếu phạm vi/phiên bản.',
    ]
    if args.provider == 'mock':
        lines.append('MOCK: chỉ kiểm tra luồng code; điểm không phản ánh ngữ nghĩa.')
    for number, question in enumerate(QUESTIONS, 1):
        filters = [None, {'audience': 'seller'}] if number == 5 else [None]
        for metadata_filter in filters:
            lines.extend(['', f'Câu {number}: {question}', f'Filter: {metadata_filter}'])
            hits = store.search_with_filter(question, top_k=3, metadata_filter=metadata_filter)
            for rank, hit in enumerate(hits, 1):
                meta = hit['metadata']
                lines.extend([
                    f"Top {rank} | score={hit['score']:.4f} | {meta['doc_id']}#{meta['chunk_index']}",
                    f"audience={meta['audience']} | source={meta['source_url']}",
                    hit['content'],
                ])
    destination = Path(args.output)
    destination.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(f'Saved: {destination.resolve()}')

if __name__ == '__main__':
    main()
