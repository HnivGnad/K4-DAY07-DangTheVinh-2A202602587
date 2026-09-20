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
| shopee_return_refund_guide_buyer | heading | 23 | 574.30 | Giữ tiêu đề cha; mục dài vẫn có thể bị chia, cần đọc các chunk liên tiếp |
| shopee_faq_return_refund_seller | fixed_size | 16 | 971.69 | Chưa đánh giá thủ công |
| shopee_faq_return_refund_seller | by_sentences | 49 | 299.41 | Chưa đánh giá thủ công |
| shopee_faq_return_refund_seller | recursive | 17 | 870.41 | Chưa đánh giá thủ công |
| shopee_faq_return_refund_seller | heading | 29 | 645.17 | Giữ tiêu đề cha; mục dài vẫn có thể bị chia, cần đọc các chunk liên tiếp |
| shopee_seller_return_refund_process | fixed_size | 7 | 943.29 | Chưa đánh giá thủ công |
| shopee_seller_return_refund_process | by_sentences | 20 | 313.25 | Chưa đánh giá thủ công |
| shopee_seller_return_refund_process | recursive | 8 | 787.88 | Chưa đánh giá thủ công |
| shopee_seller_return_refund_process | heading | 11 | 697.45 | Giữ tiêu đề cha; mục dài vẫn có thể bị chia, cần đọc các chunk liên tiếp |

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
- **Kết quả kiểm tra thủ công:** Các chunk giữ tiêu đề cha. Kiểm tra chi tiết cho thấy mục 5.1 của hướng dẫn người mua vẫn bị chia: chunk 9 chứa bước 1–6, chunk 10 chứa bước 7–8; mục 5.2 nằm trọn trong chunk 11. Vì vậy cần phân biệt giữ tiêu đề với giữ đầy đủ quy trình trong một chunk. Đây là nhận xét trên bộ dữ liệu và cấu hình hiện tại, chưa phải kết luận về chất lượng truy xuất.
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
| Đặng Thế Vinh | Heading/Section + RecursiveChunker; `chunk_size=1000` ký tự | Tạm tính 2/10 ở mức retrieval; chưa đánh giá agent | Giữ tiêu đề cha; truy xuất được một phần thông tin cần trả lời ở câu 1 và 3. | Câu 1 thiếu bước cuối; câu 3 thiếu phần danh sách; filter câu 5 không cải thiện kết quả. Câu 2, 4, 5 thiếu nguồn phù hợp. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*Với dữ liệu chính sách Shopee hiện tại, Heading/Section kết hợp Recursive là lựa chọn phù hợp vì tận dụng cấu trúc điều khoản và mục hỏi đáp. Qua kiểm tra thủ công, các chunk giữ được tiêu đề cha; một số quy trình dài vẫn trải trên nhiều chunk nên cần kiểm tra đủ ngữ cảnh khi truy xuất. Tuy nhiên, nhóm cần so sánh kết quả trên cùng 5 câu hỏi trước khi kết luận chiến lược nào truy xuất tốt nhất.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

Nhóm sử dụng đúng 5 câu hỏi dưới đây cho mọi chiến lược. Đáp án được đối chiếu với corpus; các câu thiếu nguồn chưa được chốt đáp án chuẩn. Số chunk bên dưới là chỉ số bắt đầu từ 0 trong các file `report/baseline_chunks/*__heading.txt`, ứng với cấu hình Heading 1.000 ký tự; đây là vị trí thông tin, không phải kết quả top-3. Chiến lược khác cần xác định chunk tương ứng của mình.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|---|---|---|
| 1 | Người mua cần thực hiện những bước nào trên ứng dụng Shopee để gửi yêu cầu Trả hàng/Hoàn tiền? | Theo mục 5.1 của tài liệu người mua: vào Tôi, chọn đơn trong Chờ giao hàng/Đã giao; nhấn Trả hàng/Hoàn tiền; chọn tình huống, sản phẩm, lý do và phương án xử lý; cung cấp mô tả, ảnh/video bằng chứng và email; kiểm tra rồi gửi yêu cầu. Chấp nhận cách khác theo mục 5.2: Tôi → Trò Chuyện Với Shopee → Khiếu nại trả hàng hoàn tiền → chọn đơn → xác nhận trạng thái nhận hàng, chọn lý do, tải bằng chứng → gửi yêu cầu. | `shopee_return_refund_guide_buyer`: chunk 9 + 10 chứa đầy đủ cách 5.1; chunk 11 chứa cách 5.2. |
| 2 | Khi Shopee yêu cầu bổ sung bằng chứng cho yêu cầu Trả hàng/Hoàn tiền, Người mua có bao nhiêu thời gian để phản hồi? | **Chưa chốt — thiếu nguồn xác minh.** Không dùng con số 24 giờ trong bản nháp làm gold answer. Cần tài liệu nêu thời hạn, mốc bắt đầu và điều kiện áp dụng. | Chưa xác định được chunk có nguồn đủ căn cứ trong corpus. |
| 3 | Những nhóm sản phẩm nào thuộc danh mục hạn chế không được trả hàng hoặc không áp dụng lý do "Đổi ý/không còn nhu cầu"? | **Đáp án dự kiến theo bản thu thập quy trình người bán, cần đối chiếu nguồn:** Thiết bị Điện tử & Công nghệ; Sức khỏe, Vệ sinh & Đồ cá nhân; Thực phẩm & Hàng mau hỏng; Hàng đặc thù trong vận chuyển; Sản phẩm số và dịch vụ; nhóm khác theo thông báo từng thời điểm. Danh sách này nằm trong điều kiện không áp dụng lý do Đổi ý, không có nghĩa mọi trường hợp đều bị cấm trả hàng. Hai tài liệu người mua/người bán liệt kê khác nhau nên nhóm cần thống nhất phạm vi và phiên bản trước khi chấm. | `shopee_seller_return_refund_process`: chunk 3 chứa điều kiện, chunk 4 chứa 5 nhóm chính, chunk 5 chứa nhóm khác. |
| 4 | Shopee Xu và Mã giảm giá (Voucher) đã sử dụng sẽ được hoàn lại như thế nào khi yêu cầu Trả hàng/Hoàn tiền thành công? | **Chưa chốt — thiếu nguồn xác minh.** Cần xác định riêng quy định hoàn Xu và Voucher, thời điểm, điều kiện và ngoại lệ. Không dùng kết luận tự động hoàn lại từ bản nháp làm gold answer. | Chưa xác định được chunk có nguồn đủ căn cứ trong corpus. |
| 5 | Người bán vi phạm quy định đăng bán sản phẩm trên Shopee (như bán hàng cấm, hàng giả, gian lận) sẽ bị xử lý bằng những hình thức nào? | **Chưa chốt — cần bổ sung tài liệu về xử lý vi phạm đăng bán.** Không suy đoán hình thức xử phạt và không dùng chế tài dành cho người mua trục lợi để trả lời. Chạy với `metadata_filter={"audience": "seller"}`. | Corpus hiện chưa có tài liệu đủ để xác lập đáp án. |

### Tổng hợp chất lượng truy xuất của nhóm

**Kết quả thực nghiệm của Đặng Thế Vinh:** Heading/Section kết hợp Recursive, `chunk_size=1000`, backend `gemini-embedding-001`, 6 tài liệu và 96 chunk, top-k=3. Nguồn kết quả: [ket_qua_benchmark.txt](../ket_qua_benchmark.txt). Đã chạy retrieval trên đủ 5 câu, câu 5 có thêm lượt lọc seller. Chưa sinh câu trả lời LLM, chưa có kết quả các thành viên khác nên chưa chấm điểm tổng hoặc xác định chiến lược tốt nhất.

Quy ước tên ngắn trong bảng: **buyer** = `shopee_return_refund_guide_buyer`; **process** = `shopee_seller_return_refund_process`; **faq** = `shopee_faq_return_refund_seller`; **payment** = `shopee_payment_policy_seller`. Số sau dấu # là chỉ số chunk, không phải thứ hạng.

| # | Câu hỏi | Chiến lược tốt nhất | Top-3 của Heading (chunk; score) | Đánh giá nội dung |
|---|---|---|---|---|
| 1 | Các bước gửi yêu cầu | Chưa so sánh | buyer#1 (0.8792); buyer#8 (0.8765); buyer#9 (0.8703) | Có thông tin một phần ở top-3: chunk 9 chứa bước 1–6, thiếu bước 7–8 ở chunk 10. Hai chunk đầu chỉ nêu quy định/giới thiệu, không đủ hướng dẫn hoàn chỉnh. |
| 2 | Thời hạn bổ sung bằng chứng | Chưa so sánh | buyer#3 (0.8194); process#1 (0.8170); buyer#2 (0.8083) | Không chứa đáp án cần hỏi: các đoạn nói về thời hạn gửi yêu cầu hoặc xử lý, không phải thời hạn bổ sung bằng chứng. Con số 24 giờ trong top-3 áp dụng cho yêu cầu về thực phẩm, không được dùng làm đáp án câu này. Corpus thiếu nguồn xác minh. |
| 3 | Nhóm sản phẩm hạn chế | Chưa so sánh | faq#16 (0.8910); buyer#5 (0.8596); buyer#6 (0.8489) | Có danh sách một phần ở top-3. Top-1 chỉ dẫn sang bài khác; top-2 giải thích khái niệm; top-3 chứa phần đầu bảng, thiếu phần tiếp theo ở buyer#7. Vẫn cần thống nhất phạm vi/phiên bản đáp án chuẩn. |
| 4 | Hoàn Xu và Voucher | Chưa so sánh | buyer#20 (0.7741); buyer#1 (0.7669); buyer#0 (0.7569) | Không chứa quy định hoàn Xu/Voucher. Các đoạn chỉ nói về điều kiện yêu cầu hoặc giới thiệu chung; corpus thiếu nguồn. |
| 5 | Xử lý người bán vi phạm | Chưa so sánh | faq#18 (0.7750); faq#20 (0.7495); payment#3 (0.7184), giống nhau ở cả hai lượt | Không trả lời được câu hỏi: top-1/top-2 nói về người mua trục lợi, top-3 nói về thanh toán. Chưa có nguồn xử lý vi phạm đăng bán của người bán. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

Ở câu 5, có và không có `metadata_filter={"audience": "seller"}` cho cùng ba chunk, cùng thứ hạng và điểm số; lượt thử này chưa cho thấy cải thiện. Nguyên nhân quan sát được là cả ba kết quả ban đầu đã thuộc tài liệu gắn `audience=seller`, nhưng các chunk FAQ lại bàn về hành vi của người mua: đối tượng đọc tài liệu khác với đối tượng được đề cập trong nội dung. Cần bổ sung nguồn đúng cho câu 5, cân nhắc metadata cấp chunk như `subject_role`/`topic`, và thiết kế lại thử nghiệm để chứng minh ít nhất một câu thực sự cần lọc; không đổi nhãn audience chỉ để làm kết quả đẹp hơn.

**Phân tích lỗi thực tế:** Câu 1 lấy đúng tài liệu nhưng thiếu bước cuối vì mục 5.1 bị chia thành chunk 9 và 10, trong khi hai đoạn giới thiệu chiếm top-1/top-2. Hướng cải thiện cần thử là giữ nguyên toàn bộ mục hướng dẫn khi phù hợp, lấy thêm chunk liền kề hoặc xếp hạng lại để ưu tiên đoạn chứa bước thao tác. Câu 3 cũng cho thấy chunk có tiêu đề gần giống câu hỏi có thể xếp cao dù chỉ chứa lời dẫn sang tài liệu khác. Đây là đề xuất thử nghiệm, chưa phải cải thiện đã được đo.

**Giới hạn đánh giá:** Có thông tin trả lời một phần ở câu 1 và 3; top-3 chưa đủ trả lời trọn vẹn cả 5 câu. Không quy toàn bộ lỗi cho Heading vì câu 2, 4, 5 thiếu dữ liệu nguồn. Chưa đánh giá chất lượng câu trả lời agent hoặc chấm điểm theo rubric khi chưa có câu trả lời và gold answer đầy đủ.

**Lưu ý khi nạp dữ liệu:** Chỉ nạp tài liệu được liệt kê trong `sources.csv`. `SHOPEE_DATA_REVIEW.md` là ghi chú rà soát, không phải nguồn chính sách và không được nạp vào benchmark.

---
## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

- **Điểm tương đồng cao không đồng nghĩa có đủ đáp án.** Ở câu 1, top-1 đạt 0.8792 nhưng chỉ chứa quy định chung; đoạn hướng dẫn đứng top-3 và thiếu bước 7–8. Ở câu 3, top-1 đạt 0.8910 nhưng chỉ dẫn sang bài khác, cho thấy cần kiểm tra nội dung trả lời được thay vì chỉ nhìn điểm hoặc tên tài liệu.
- **Giữ tiêu đề chưa đủ để giữ trọn quy trình.** HeadingChunker giữ tiêu đề cha nhưng ngưỡng 1.000 ký tự vẫn chia mục 5.1 thành chunk 9 và 10; chỉ chunk 9 được truy xuất. Đây là trường hợp lỗi cụ thể để thử giữ nguyên mục hướng dẫn hoặc lấy thêm chunk liền kề.
- **Metadata phải phân biệt người đọc với đối tượng được nói đến.** Câu 5 có/không filter `audience=seller` trả về cùng top-3, vì tài liệu dành cho người bán vẫn có đoạn nói về người mua trục lợi. Filter không bổ sung được thông tin còn thiếu trong corpus; câu 2, 4, 5 cần nguồn phù hợp trước khi đánh giá đầy đủ.

**Bài học rút ra khi so sánh trong nhóm:**

Trên cùng tài liệu hướng dẫn người mua, baseline tạo 12 chunk FixedSize, 30 chunk Sentence, 16 chunk Recursive và 23 chunk Heading, cho thấy cách chia làm thay đổi số lượng và phạm vi nội dung của mỗi đơn vị truy xuất. Kết quả Heading cho thấy giữ cấu trúc tiêu đề giúp nhận diện ngữ cảnh nhưng chưa bảo đảm lấy đủ các bước hoặc danh sách khi một mục trải trên nhiều chunk. Nhóm hiện mới có benchmark retrieval của Heading, nên chưa kết luận chiến lược nào tốt nhất; cần so sánh các thành viên trên cùng corpus, câu hỏi, backend embedding và top-k.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

Nhóm sẽ lập bảng đối chiếu từng câu hỏi với đoạn nguồn và đáp án chuẩn trước khi chạy benchmark, ưu tiên bổ sung nguồn cho câu 2, 4, 5 và thống nhất phạm vi/phiên bản của danh mục hạn chế ở câu 3. Nhóm sẽ chuẩn hóa heading, giữ đủ điều kiện và ngoại lệ, đồng thời bổ sung metadata cấp chunk về chủ đề hoặc đối tượng được đề cập khi cần phân biệt với `audience` của tài liệu. Sau đó, nhóm sẽ thử giữ trọn mục hướng dẫn hoặc mở rộng sang chunk liền kề và đo lại trên cùng bộ câu hỏi để kiểm chứng hiệu quả.

---

## Tự Đánh Giá (Phần Nhóm)

Đây là mức tự đánh giá tạm thời dựa trên minh chứng hiện có, không phải điểm giảng viên hoặc kết quả đã hoàn tất của cả nhóm. Điểm sẽ được cập nhật sau khi bổ sung nguồn, kết quả các thành viên, câu trả lời agent và demo.

| Tiêu chí | Điểm tự đánh giá | Căn cứ và phần còn thiếu |
|----------|-------------------|-------------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 | Có 6 tài liệu cùng chủ đề, URL nguồn, metadata và sources.csv; đã chuẩn hóa heading. |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 | Có baseline ba chiến lược trên ba tài liệu, triển khai Heading + Recursive, giải thích lựa chọn và phân tích lỗi thực tế. |
| Chất lượng truy xuất (Retrieval Quality) | 7 / 10 | Đây chỉ là ước lượng ở mức retrieval, chưa có câu trả lời agent và gold answer đầy đủ để chốt điểm theo rubric. |
| Thuyết trình (Demo) | 0 / 5 | Đã chuẩn bị insights, bài học và hướng cải thiện; chưa có minh chứng về buổi demo và phần trình bày của từng thành viên. |
| **Tổng phần nhóm** | **32 điểm; tối đa 40** | **32 trên 40 điểm của ba mục đã ước lượng ** |
