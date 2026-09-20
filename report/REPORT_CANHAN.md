# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Đặng Thế Vinh]
**Nhóm:** [VGV]
**Ngày:** [20/09]

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
> Mỗi document được chuyển thành vector embedding, sau đó lưu trong bộ nhớ cùng ID, nội dung và metadata. Khi tìm kiếm, câu hỏi được chuyển thành vector bằng cùng hàm embedding; tính tích vô hướng với từng vector đã lưu (tương đương cosine nếu các vector được chuẩn hóa về độ dài 1). Sắp xếp điểm giảm dần và trả về top_k kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Lọc các document theo metadata trước khi tính độ tương tự, rồi tìm top_k trong tập đã lọc để tránh kết quả sai đối tượng. Khi xóa, loại bỏ tất cả chunk có metadata["doc_id"] khớp với doc_id được yêu cầu. Trả về True nếu có chunk bị xóa, ngược lại trả về False.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Truy xuất top_k chunk liên quan đến câu hỏi rồi ghép nội dung thành phần ngữ cảnh. Prompt gồm chỉ dẫn trả lời dựa trên tài liệu, ngữ cảnh truy xuất và câu hỏi; yêu cầu thông báo thiếu thông tin nếu ngữ cảnh không đủ để trả lời. Cuối cùng, truyền prompt vào llm_fn và trả về câu trả lời nhận được.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED      [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED     [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED            [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED       [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED   [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED             [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED            [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED      [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED       [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED      [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED  [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

================================== 42 passed in 0.06s ==================================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Tôi muốn trả lại sản phẩm. | Tôi muốn gửi trả món hàng đã mua. | Cao | 0.8969 | Có |
| 2 | Sản phẩm được bảo hành trong 12 tháng. | Thời hạn bảo hành của sản phẩm là một năm. | Cao | 0.9008 | Có |
| 3 | Người mua được hoàn tiền khi đơn hàng bị hủy. | Khi đơn hàng bị hủy, tiền sẽ được trả lại cho người mua. | Cao | 0.9473 | Có |
| 4 | Tôi muốn yêu cầu hoàn tiền. | Hôm nay trời nắng đẹp. | Thấp | 0.5977 | Không |
| 5 | Người bán cần xác nhận đơn hàng. | Tôi đang học cách nấu canh chua. | Thấp | 0.5636 | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 4 khiến tôi bất ngờ nhất vì hai câu khác chủ đề nhưng có điểm 0.5977, vượt ngưỡng 0,5 đã chọn. Tuy nhiên, cả hai cặp khác chủ đề vẫn có điểm thấp hơn rõ rệt so với ba cặp diễn đạt cùng ý, cho thấy mô hình phân biệt được mức độ tương đồng trong các ví dụ này. Kết quả cũng cho thấy ngưỡng 0,5 chưa phù hợp để phân loại bộ câu này; điểm cosine không phải tỷ lệ phần trăm giống nhau về ý nghĩa.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Tôi chạy cùng 5 câu hỏi đã thống nhất trong báo cáo nhóm trên mã nguồn cá nhân. Cấu hình: **Heading/Section kết hợp RecursiveChunker, 1.000 ký tự/chunk, Gemini `gemini-embedding-001`, 6 tài liệu, 96 chunk và top-k=3**. Dữ liệu được nạp theo `sources.csv`, bỏ frontmatter khỏi nội dung và giữ metadata trên từng chunk; vector được chuẩn hóa trước khi tính điểm.

Minh chứng: [ket_qua_benchmark.txt](../ket_qua_benchmark.txt). Lệnh chạy:

```powershell
.\.venv-heading\Scripts\python.exe bench.py --provider gemini --strategy heading --output ket_qua_benchmark.txt
```

**Phạm vi kết quả:** Lần chạy này chỉ truy xuất, chưa gọi LLM sinh câu trả lời. Vì vậy cột Agent được ghi là chưa chạy, không sử dụng đáp án tự viết thay cho kết quả thực nghiệm.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|---|---|---:|---|---|
| 1 | Người mua cần thực hiện những bước nào trên ứng dụng Shopee để gửi yêu cầu Trả hàng/Hoàn tiền? | `shopee_return_refund_guide_buyer#1`: quy định chung về đổi sản phẩm, đồng kiểm và gửi yêu cầu trên ứng dụng. | 0.8792 | Đúng chủ đề, nhưng top-1 không chứa các bước thao tác. | Chưa chạy LLM. |
| 2 | Khi Shopee yêu cầu bổ sung bằng chứng cho yêu cầu Trả hàng/Hoàn tiền, Người mua có bao nhiêu thời gian để phản hồi? | `shopee_return_refund_guide_buyer#3`: thời hạn gửi yêu cầu và thời gian hệ thống phản hồi. | 0.8194 | Không trả lời đúng loại thời hạn được hỏi. | Chưa chạy LLM. |
| 3 | Những nhóm sản phẩm nào thuộc danh mục hạn chế không được trả hàng hoặc không áp dụng lý do "Đổi ý/không còn nhu cầu"? | `shopee_faq_return_refund_seller#16`: hướng người đọc sang bài quy trình để xem danh sách hạn chế. | 0.8910 | Đúng chủ đề, nhưng không chứa danh sách sản phẩm. | Chưa chạy LLM. |
| 4 | Shopee Xu và Mã giảm giá (Voucher) đã sử dụng sẽ được hoàn lại như thế nào khi yêu cầu Trả hàng/Hoàn tiền thành công? | `shopee_return_refund_guide_buyer#20`: khả năng gửi yêu cầu sau khi đã nhấn Đã nhận được hàng. | 0.7741 | Không chứa quy định hoàn Xu hoặc Voucher. | Chưa chạy LLM. |
| 5 | Người bán vi phạm quy định đăng bán sản phẩm trên Shopee (như bán hàng cấm, hàng giả, gian lận) sẽ bị xử lý bằng những hình thức nào? | `shopee_faq_return_refund_seller#18`: chế tài đối với người mua trục lợi; kết quả khi lọc `audience=seller`. | 0.7750 | Sai đối tượng bị xử lý; không trả lời về vi phạm đăng bán của người bán. | Chưa chạy LLM. |

### Kết quả top-3 và đối chiếu nội dung

Tên ngắn: **buyer** = `shopee_return_refund_guide_buyer`; **process** = `shopee_seller_return_refund_process`; **faq** = `shopee_faq_return_refund_seller`; **payment** = `shopee_payment_policy_seller`. Số sau # là chỉ số chunk bắt đầu từ 0.

| Câu | Top-1 (score) | Top-2 (score) | Top-3 (score) | Nhận xét |
|---|---|---|---|---|
| 1 | buyer#1 (0.8792) | buyer#8 (0.8765) | buyer#9 (0.8703) | Có bước 1–6 ở top-3, thiếu bước 7–8 trong buyer#10. |
| 2 | buyer#3 (0.8194) | process#1 (0.8170) | buyer#2 (0.8083) | Không có thời hạn bổ sung bằng chứng. Con số 24 giờ trong buyer#2 là thời hạn yêu cầu với thực phẩm, không phải đáp án câu này. |
| 3 | faq#16 (0.8910) | buyer#5 (0.8596) | buyer#6 (0.8489) | Có một phần danh sách ở top-3, thiếu phần tiếp theo trong buyer#7; cần đối chiếu phạm vi/phiên bản gold answer. |
| 4 | buyer#20 (0.7741) | buyer#1 (0.7669) | buyer#0 (0.7569) | Không có nội dung trả lời về hoàn Xu/Voucher. |
| 5 | faq#18 (0.7750) | faq#20 (0.7495) | payment#3 (0.7184) | Giống nhau khi có/không filter seller; không có chế tài đăng bán cần hỏi. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **2 / 5**, nếu tính chunk thực sự chứa ít nhất một phần thông tin trả lời: câu 1 và câu 3. Cả hai vẫn thiếu thông tin để trả lời trọn vẹn; con số này không phải tỷ lệ câu trả lời Agent đúng. Câu 2, 4, 5 thiếu nguồn phù hợp trong corpus nên chưa thể quy lỗi hoàn toàn cho chiến lược chunking.

### Thử nghiệm metadata filter

Tôi chạy câu 5 hai lần: không lọc và lọc `audience=seller`. Cả hai cho cùng top-3, thứ hạng và điểm số nên filter chưa cải thiện kết quả trong lần thử này. Tài liệu dành cho người bán vẫn chứa đoạn nói về người mua trục lợi; vì vậy cần phân biệt đối tượng đọc tài liệu với đối tượng được đề cập, bổ sung nguồn đúng và cân nhắc metadata cấp chunk như `subject_role` hoặc `topic`.

### Trường hợp lỗi và hướng cải thiện

Ở câu 1, hai đoạn quy định/giới thiệu chiếm top-1 và top-2, trong khi đoạn hướng dẫn chỉ đứng top-3 và bị thiếu bước cuối vì mục 5.1 trải trên hai chunk. Tôi sẽ thử giữ nguyên mục hướng dẫn hoặc lấy thêm chunk liền kề, sau đó đo lại trên cùng bộ câu hỏi để kiểm chứng. Câu 3 cũng cho thấy tiêu đề giống câu hỏi có thể tạo điểm cao dù nội dung chỉ dẫn sang bài khác; cần kiểm tra thông tin thực sự có trong chunk thay vì chỉ nhìn cosine score.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

Điều tôi thấy đáng học hỏi khi đối chiếu các cách chia là phải kiểm tra chunk có chứa đủ đáp án, thay vì chỉ nhìn điểm tương đồng hoặc tên tài liệu. Overlap là một hướng đáng thử để giữ thông tin ở ranh giới chunk, còn chia theo heading giúp giữ cấu trúc mục; mỗi cách đều cần được kiểm chứng trên cùng câu hỏi. Tôi cũng nhận ra metadata phải phản ánh đúng nhu cầu lọc, vì tài liệu dành cho người bán vẫn có thể nói về hành vi của người mua.


---
## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá | Căn cứ |
|----------|-------------------|--------|
| Khởi động (Warm-up) | 5 / 5 | Giải thích cosine, có ví dụ tương đồng cao/thấp, so sánh với Euclid và tính đúng số chunk khi thay đổi overlap. |
| Hướng tiếp cận của tôi (My Approach) | 8 / 10 | Đã giải thích Sentence, Recursive, store, filter, delete và agent; phần 5 mô tả Heading. Cần bổ sung giải thích riêng cho compute_similarity và ChunkingStrategyComparator để đầy đủ hơn. |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 | Báo cáo đã lưu output 42/42 tests passed. Điểm này dựa trên kết quả kiểm thử đã ghi nhận, không thay thế đánh giá chất lượng retrieval. |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 | Có 5 cặp câu, dự đoán, điểm thực tế và phân tích trường hợp bất ngờ; giải thích hạn chế của ngưỡng 0,5. Dự đoán không trùng kết quả vẫn có giá trị nếu phân tích đúng. |
| Kết quả truy xuất của tôi (Competition Results) | 7 / 10 | Đã chạy đủ 5 câu hỏi chung bằng Gemini, lưu top-3 và điểm, thử filter A/B, phân tích lỗi và hướng cải thiện. Chưa sinh câu trả lời agent; câu 2, 4, 5 thiếu nguồn và câu 3 cần chốt phạm vi/phiên bản đáp án. |
| **Tổng phần cá nhân** | **55 / 60 (tạm tính)** | **5 + 8 + 30 + 5 + 7 = 55.** |
