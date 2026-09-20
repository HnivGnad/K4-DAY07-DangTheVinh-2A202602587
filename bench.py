from src.heading_chunking import HeadingChunker
from src.models import Document
from src.store import EmbeddingStore

# Dữ liệu giả lập để kiểm tra luồng code, không phải chính sách Shopee.
doc_id = "tai-lieu-thu"

metadata = {
    "audience": "buyer",
    "category": "demo",
    "language": "vi",
}

body = """
# Tài liệu thử

## Gửi yêu cầu
Đây là nội dung thử cho mục gửi yêu cầu.

## Bổ sung bằng chứng
Đây là nội dung thử cho mục bổ sung bằng chứng.
"""

# Mặc định sử dụng mock embedding để kiểm tra code.
store = EmbeddingStore(collection_name="heading_demo")
chunker = HeadingChunker(chunk_size=1000)

documents = [
    Document(
        id=f"{doc_id}#{index}",
        content=chunk,
        metadata={
            **metadata,
            "doc_id": doc_id,
            "chunk_index": index,
        },
    )
    for index, chunk in enumerate(chunker.chunk(body))
]

store.add_documents(documents)

print(f"Đã nạp {store.get_collection_size()} chunk")

for document in documents:
    print(f"\n--- {document.id} ---")
    print(document.content)

question = "Cần bổ sung bằng chứng như thế nào?"

results = store.search_with_filter(
    question,
    top_k=3,
    metadata_filter={"audience": "buyer"},
)

print(f"\nCâu hỏi: {question}")

for rank, result in enumerate(results, start=1):
    print(f"\nTop {rank} | Điểm: {result['score']:.4f}")
    print("Tài liệu:", result["metadata"]["doc_id"])
    print(result["content"])