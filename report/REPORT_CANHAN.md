# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Đặng Thế Vinh
**Nhóm:** VGV
**Ngày:** 20/09

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai vector biểu diễn văn bản có hướng gần nhau, thường cho thấy hai văn bản tương đồng về nội dung hoặc ngữ nghĩa. Chỉ số càng gần 1 thì mức độ tương đồng càng cao.

**Ví dụ có độ tương tự CAO:**
>- Câu A: Tôi muốn trả lại sản phẩm và nhận lại tiền.
>- Câu B: Tôi muốn hoàn tiền cho món hàng đã mua bằng cách gửi trả hàng.
>- Tại sao tương đồng: Cả hai câu đều diễn đạt mong muốn trả hàng để được hoàn tiền, dù cách dùng từ khác nhau.

**Ví dụ có độ tương tự THẤP:**
>- Câu A: Tôi muốn trả lại sản phẩm và nhận lại tiền.
>- Câu B: Hôm nay trời nắng, rất thích hợp để đi dạo.
>- Tại sao khác: Câu A nói về đổi trả hàng và hoàn tiền, còn câu B nói về thời tiết và hoạt động ngoài trời.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity đo sự tương đồng về hướng của các vector, không bị ảnh hưởng bởi độ lớn nên thường phù hợp để so sánh ngữ nghĩa văn bản. Khoảng cách Euclid chịu ảnh hưởng của cả hướng lẫn độ lớn; khi các vector được chuẩn hóa về độ dài 1, hai cách đo cho thứ tự tương đồng tương đương.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính: Số chunk = ⌈(10.000 − 50) / (500 − 50)⌉ = ⌈9.950 / 450⌉ = ⌈22,11⌉.
> Đáp án: 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, số chunk là ⌈(10.000 − 100)/(500 − 100)⌉ = 25, tăng 2 chunk so với trước. Chồng chéo nhiều hơn giúp giữ ngữ cảnh tại ranh giới giữa các chunk, nhưng làm tăng dữ liệu trùng lặp và chi phí xử lý.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex r"(?<=[.!?])\s+" để tách câu tại khoảng trắng hoặc xuống dòng sau dấu ., !, ?, đồng thời giữ lại dấu câu. Sau đó, tôi loại bỏ khoảng trắng đầu/cuối và các phần rỗng, rồi ghép các câu thành từng chunk theo max_sentences_per_chunk. Với văn bản rỗng, kết quả dự kiến là danh sách rỗng; số câu mỗi chunk được giới hạn tối thiểu là 1.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Tôi chia văn bản theo thứ tự ưu tiên của các dấu phân cách: đoạn văn, dòng, câu rồi khoảng trắng; phần còn quá dài được xử lý đệ quy với dấu phân cách tiếp theo. Các phần nhỏ được ghép lại nếu tổng độ dài không vượt chunk_size, đồng thời giữ dấu phân cách để không mất nội dung. Trường hợp cơ sở là văn bản rỗng trả về [], văn bản đủ ngắn trả về một chunk; khi hết dấu phân cách hoặc gặp dấu phân cách rỗng, tôi cắt trực tiếp theo số ký tự.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?*

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?*

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?*

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: pytest tests/ -v
```

**Số lượng bài test vượt qua (pass):** __ / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
