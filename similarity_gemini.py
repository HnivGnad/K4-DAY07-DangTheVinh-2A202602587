import os
from pathlib import Path

from dotenv import load_dotenv
from src.embeddings import GeminiEmbedder
from src.chunking import compute_similarity

load_dotenv(Path(__file__).resolve().parent / ".env")

pairs = [
    ("Tôi muốn trả lại sản phẩm.",
     "Tôi muốn gửi trả món hàng đã mua.", "cao"),
    ("Sản phẩm được bảo hành trong 12 tháng.",
     "Thời hạn bảo hành của sản phẩm là một năm.", "cao"),
    ("Người mua được hoàn tiền khi đơn hàng bị hủy.",
     "Khi đơn hàng bị hủy, tiền sẽ được trả lại cho người mua.", "cao"),
    ("Tôi muốn yêu cầu hoàn tiền.",
     "Hôm nay trời nắng đẹp.", "thấp"),
    ("Người bán cần xác nhận đơn hàng.",
     "Tôi đang học cách nấu canh chua.", "thấp"),
]

embedder = GeminiEmbedder(
    model_name=os.getenv(
        "GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"
    )
)

print("Backend:", embedder._backend_name)

# Ngưỡng quy ước cho bài thực nghiệm, không phải chuẩn chung.
threshold = 0.5

for i, (a, b, prediction) in enumerate(pairs, 1):
    score = compute_similarity(embedder(a), embedder(b))
    actual = "cao" if score >= threshold else "thấp"
    correct = "Có" if prediction == actual else "Không"

    print(
        f"Cặp {i}: dự đoán={prediction}, "
        f"điểm={score:.4f}, đúng={correct}"
    )