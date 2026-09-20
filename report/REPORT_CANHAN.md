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
