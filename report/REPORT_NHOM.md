# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [VGV]
**Thành viên:** [Nguyễn Thành Vinh - Nguyễn Thanh Giang - Đặng Thế Vinh]
**Ngày:** [20/09]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách bảo hành, đổi trả dành cho người mua và người bán trên Shopee

**Tại sao nhóm chọn chủ đề này?**
> Chính sách đổi trả/bảo hành là loại tài liệu có cấu trúc rõ ràng (có điều khoản, mục, danh sách), đồng thời có sự phân tách tự nhiên giữa 2 nhóm người dùng (buyer/seller) — rất phù hợp để kiểm thử metadata filter. Ngoài ra, nội dung công khai, dễ thu thập, và câu hỏi thực tế của người dùng Shopee rất cụ thể nên dễ đánh giá chất lượng retrieval.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | shopee_faq_return_refund_seller | https://banhang.shopee.vn/edu/article/10626 | 2026-09-20 / 20-08-2026 | 14801 | audience=seller, category=return_refund_faq |
| 2 | shopee_payment_policy_seller | https://banhang.shopee.vn/edu/article/234 | 2026-09-20 / 18-05-2026 | 6396 | audience=seller, category=payment |
| 3 | shopee_return_refund_guide_buyer | https://shopee.vn/blog/cach-tra-hang-hoan-tien-tren-shopee/ | 2026-09-20 / 15-09-2026 | 11277 | audience=buyer, category=return_refund_guide |
| 4 | shopee_return_shipping_fee_policy | https://banhang.shopee.vn/edu/article/3648 | 2026-09-20 / 16-09-2025 | 4714 | audience=seller, category=return_refund |
| 5 | shopee_seller_return_refund_process | https://banhang.shopee.vn/edu/article/563 | 2026-09-20 / 2026-08-27 | 6303 | audience=seller, category=return_refund |
| 6 | shopee_warranty_policy | https://help.shopee.vn/portal/4/article/79046-[Quy-%C4%91%E1%BB%8Bnh]-Ch%C3%ADnh-s%C3%A1ch-b%E1%BA%A3o-h%C3%A0nh-cho-s%E1%BA%A3n-ph%E1%BA%A9m-mua-t%E1%BA%A1i-Shopee | 2026-09-20 / not-stated | 4302 | audience=buyer, category=warranty |

> Số ký tự tính trên phần thân đã bỏ frontmatter, khoảng trắng đầu/cuối; xuống dòng LF. Danh sách nguồn: `data/shopee/sources.csv`.
>
> Chưa đủ nguồn để chốt đáp án câu 2, 4, 5. Xem [ghi chú rà soát](SHOPEE_DATA_REVIEW.md).

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `shopee_warranty_policy` | Định danh duy nhất — dùng để xóa hoặc cập nhật document trong store |
| `title` | string | `Chính sách bảo hành...` | Hiển thị cho người dùng cuối, giúp trace kết quả về nguồn |
| `source_url` | string | `https://banhang.shopee.vn/...` | Truy vết nguồn gốc câu trả lời, đảm bảo tính minh bạch |
| `retrieved_at` | string (ISO date) | `2026-09-20` | Kiểm tra độ mới của thông tin (chính sách thay đổi thường xuyên) |
| `document_version` | string | `20-08-2026` | Xác định phiên bản chính sách đang áp dụng |
| `audience` | string enum | `buyer` / `seller` / `both` | **Filter chính** — tránh trả kết quả buyer cho câu hỏi seller và ngược lại |
| `category` | string | `return_refund`, `warranty`, `payment` | Lọc theo chủ đề cụ thể, thu hẹp không gian tìm kiếm |
| `language` | string | `vi` | Hỗ trợ mở rộng đa ngôn ngữ trong tương lai |

---


## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Đã chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu sau khi tách frontmatter; chạy thêm `HeadingChunker` trên cùng nội dung để đối chiếu.

**Cấu hình:** FixedSize, Recursive và Heading dùng `chunk_size=1000` ký tự; FixedSize dùng `overlap=50`; Sentence nhóm 3 câu/chunk và không giới hạn số ký tự. Độ dài của Heading bao gồm tiêu đề được lặp lại trong các chunk con.

Số liệu lấy từ [BASELINE_RESULTS.md](BASELINE_RESULTS.md); các chunk được lưu trong `report/baseline_chunks/`. Nhận xét Heading dựa trên kiểm tra thủ công của Đặng Thế Vinh; ba chiến lược còn lại chưa có nhận xét thủ công.

| Tài liệu | Chiến lược | Số lượng chunk | Độ dài trung bình (ký tự) | Giữ được ngữ cảnh không? |
|---|---|---:|---:|---|
| shopee_return_refund_guide_buyer | fixed_size | 12 | 985.58 | Chưa đánh giá thủ công |
| shopee_return_refund_guide_buyer | by_sentences | 30 | 374.37 | Chưa đánh giá thủ công |
| shopee_return_refund_guide_buyer | recursive | 16 | 704.81 | Chưa đánh giá thủ công |
| shopee_return_refund_guide_buyer | heading | 23 | 574.30 | Có — giữ tiêu đề cha, các bước hướng dẫn và ngữ cảnh (đã kiểm tra thủ công) |
| shopee_faq_return_refund_seller | fixed_size | 16 | 971.69 | Chưa đánh giá thủ công |
| shopee_faq_return_refund_seller | by_sentences | 49 | 299.41 | Chưa đánh giá thủ công |
| shopee_faq_return_refund_seller | recursive | 17 | 870.41 | Chưa đánh giá thủ công |
| shopee_faq_return_refund_seller | heading | 29 | 645.17 | Có — giữ tiêu đề cha, các bước hướng dẫn và ngữ cảnh (đã kiểm tra thủ công) |
| shopee_seller_return_refund_process | fixed_size | 7 | 943.29 | Chưa đánh giá thủ công |
| shopee_seller_return_refund_process | by_sentences | 20 | 313.25 | Chưa đánh giá thủ công |
| shopee_seller_return_refund_process | recursive | 8 | 787.88 | Chưa đánh giá thủ công |
| shopee_seller_return_refund_process | heading | 11 | 697.45 | Có — giữ tiêu đề cha, các bước hướng dẫn và ngữ cảnh (đã kiểm tra thủ công) |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — Đặng Thế Vinh**

- **Loại chiến lược:** Heading/Section kết hợp RecursiveChunker (custom).
- **Tham số:** `chunk_size=1000` ký tự, bao gồm tiêu đề trong chunk; phần thân được chia tiếp theo ngân sách ký tự còn lại.
- **Mô tả & lý do chọn:** Chia nội dung theo tiêu đề Markdown và giữ hệ thống tiêu đề cha trong từng chunk. Với mục dài, dùng RecursiveChunker để chia tiếp và gắn lại tiêu đề vào từng mảnh. Cách này phù hợp với tài liệu chính sách có điều khoản, quy trình và các mục hỏi đáp rõ ràng.
- **Kết quả kiểm tra thủ công:** Trên các file Heading đã kiểm tra, chunk vẫn giữ tiêu đề cha, các bước hướng dẫn không bị tách rời và ngữ cảnh được bảo toàn. Đây là nhận xét trên bộ dữ liệu và cấu hình hiện tại, chưa phải kết luận về chất lượng truy xuất.
- **Hạn chế:** Tiêu đề lặp lại chiếm một phần dung lượng chunk; mục quá dài vẫn có thể bị chia giữa các điều kiện hoặc bước. Hiệu quả phụ thuộc việc chuẩn hóa heading của tài liệu đầu vào.
- **Mã triển khai:** [src/heading_chunking.py](../src/heading_chunking.py).
- **Cách sử dụng (sau khi tách frontmatter):**

```python
from src.heading_chunking import HeadingChunker

chunker = HeadingChunker(chunk_size=1000)
chunks = chunker.chunk(body)  # body là nội dung Markdown đã bỏ frontmatter
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| Đặng Thế Vinh | Heading/Section + RecursiveChunker; `chunk_size=1000` ký tự | Chờ benchmark | Qua kiểm tra thủ công các chunk: giữ tiêu đề cha, các bước hướng dẫn không bị tách rời và vẫn giữ ngữ cảnh. | Chưa xác định lỗi truy xuất qua benchmark. Hạn chế thiết kế: phụ thuộc cấu trúc heading; tiêu đề lặp lại chiếm dung lượng chunk, mục quá dài vẫn có thể bị chia nhỏ. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
