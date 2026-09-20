"""Compare chunking strategies on three Shopee documents; no API needed."""

from pathlib import Path
import argparse
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.chunking import ChunkingStrategyComparator
from src.heading_chunking import HeadingChunker


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunk-size", type=int, default=1000)
    args = parser.parse_args()
    if args.chunk_size <= 0:
        parser.error("--chunk-size must be positive")

    names = [
        "shopee_return_refund_guide_buyer",
        "shopee_faq_return_refund_seller",
        "shopee_seller_return_refund_process",
    ]
    output = ROOT / "report" / "baseline_chunks"
    output.mkdir(parents=True, exist_ok=True)
    table = [
        "# Kết quả baseline chunking",
        "",
        f"FixedSize, Recursive và Heading dùng chunk_size={args.chunk_size} ký tự. "
        f"FixedSize overlap={min(50, args.chunk_size - 1)}; Sentence nhóm 3 câu, "
        "không giới hạn số ký tự. Heading tính cả tiêu đề lặp lại vào độ dài chunk.",
        "",
        "Đã bỏ frontmatter. Đây là thống kê chunking, chưa phải điểm retrieval. "
        "Đọc các file trong baseline_chunks/ để tự đánh giá ngữ cảnh.",
        "",
        "| Tài liệu | Chiến lược | Số chunk | Độ dài trung bình | Giữ ngữ cảnh? |",
        "|---|---|---:|---:|---|",
    ]
    for name in names:
        path = ROOT / "data" / "shopee" / f"{name}.md"
        text = path.read_text(encoding="utf-8-sig")
        match = re.match(r"\A---\s*\n.*?\n---\s*(?:\n|$)", text, re.DOTALL)
        if not match:
            raise ValueError(f"Missing frontmatter: {path}")
        body = text[match.end():].strip()
        results = ChunkingStrategyComparator().compare(body, args.chunk_size)
        chunks = HeadingChunker(args.chunk_size).chunk(body)
        results["heading"] = {
            "count": len(chunks),
            "avg_length": sum(map(len, chunks)) / len(chunks) if chunks else 0,
            "chunks": chunks,
        }
        for strategy, result in results.items():
            table.append(
                f"| {name} | {strategy} | {result['count']} | "
                f"{result['avg_length']:.2f} | Cần đọc chunk |"
            )
            preview = "\n\n".join(
                f"===== CHUNK {i} | {len(chunk)} ký tự =====\n{chunk}"
                for i, chunk in enumerate(result["chunks"])
            )
            (output / f"{name}__{strategy}.txt").write_text(
                preview + "\n", encoding="utf-8"
            )
    report = ROOT / "report" / "BASELINE_RESULTS.md"
    report.write_text("\n".join(table) + "\n", encoding="utf-8")
    print(f"Results: {report}")
    print(f"Chunk previews: {output}")


if __name__ == "__main__":
    main()
