# Kết quả baseline chunking

FixedSize, Recursive và Heading dùng chunk_size=1000 ký tự. FixedSize overlap=50; Sentence nhóm 3 câu, không giới hạn số ký tự. Heading tính cả tiêu đề lặp lại vào độ dài chunk.

Đã bỏ frontmatter. Đây là thống kê chunking, chưa phải điểm retrieval. Đọc các file trong baseline_chunks/ để tự đánh giá ngữ cảnh.

| Tài liệu | Chiến lược | Số chunk | Độ dài trung bình | Giữ ngữ cảnh? |
|---|---|---:|---:|---|
| shopee_return_refund_guide_buyer | fixed_size | 12 | 985.58 | Cần đọc chunk |
| shopee_return_refund_guide_buyer | by_sentences | 30 | 374.37 | Cần đọc chunk |
| shopee_return_refund_guide_buyer | recursive | 16 | 704.81 | Cần đọc chunk |
| shopee_return_refund_guide_buyer | heading | 23 | 574.30 | Cần đọc chunk |
| shopee_faq_return_refund_seller | fixed_size | 16 | 971.69 | Cần đọc chunk |
| shopee_faq_return_refund_seller | by_sentences | 49 | 299.41 | Cần đọc chunk |
| shopee_faq_return_refund_seller | recursive | 17 | 870.41 | Cần đọc chunk |
| shopee_faq_return_refund_seller | heading | 29 | 645.17 | Cần đọc chunk |
| shopee_seller_return_refund_process | fixed_size | 7 | 943.29 | Cần đọc chunk |
| shopee_seller_return_refund_process | by_sentences | 20 | 313.25 | Cần đọc chunk |
| shopee_seller_return_refund_process | recursive | 8 | 787.88 | Cần đọc chunk |
| shopee_seller_return_refund_process | heading | 11 | 697.45 | Cần đọc chunk |
