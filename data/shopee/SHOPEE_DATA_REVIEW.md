# Rà soát dữ liệu Shopee

Không nạp report/ vào vector store. Corpus chỉ gồm các file Markdown trong data/shopee/.

## Đã chỉnh sửa

- Thêm heading vào quy trình người bán, giữ nguyên nội dung điều khoản và danh sách.
- Xóa comment mã Python khỏi FAQ người bán.
- Phiên bản bảo hành dùng not-stated vì bản thu thập chưa cung cấp phiên bản; chưa xác minh rằng trang gốc không có phiên bản.
- Tạo sources.csv khớp các file; cập nhật số ký tự phần thân trong báo cáo nhóm.

## Còn cần bổ sung hoặc đối chiếu

- Câu 1: có hướng dẫn thao tác trong tài liệu người mua.
- Câu 2: cần nguồn xác nhận thời hạn bổ sung bằng chứng; chưa chốt gold answer.
- Câu 3: hai danh sách khác phạm vi/phiên bản, cần đối chiếu. Không gộp danh sách hoặc coi hạn chế lý do đổi ý là cấm mọi trường hợp trả hàng.
- Câu 4: cần nguồn hoàn Xu và Voucher, gồm điều kiện và ngoại lệ; chưa chốt gold answer.
- Câu 5: bổ sung tài liệu xử lý vi phạm đăng bán, audience=seller. Không dùng chế tài dành cho người mua trục lợi.
- Các trang Seller Education Hub và bảo hành chưa được công cụ đọc đầy đủ; nhóm cần đối chiếu nội dung và ngày của bản thu thập với nguồn.
- Quy trình người bán ghi ngày cập nhật 20-08-2026 và ngày hiệu lực 27/08/2026. Metadata dùng ngày hiệu lực; không tự đồng nhất hai ngày.

## Hai đoạn tạm tách khỏi corpus — CHƯA XÁC MINH

Hai đoạn dưới đây có trong bản Markdown nhưng không tìm thấy trong văn bản trang Shopee Blog đã đọc. Giữ để truy vết, không dùng làm gold answer hay nạp vào benchmark trước khi có nguồn chứng minh. Chưa kết luận nội dung chắc chắn sai.

Nguồn đã đối chiếu: https://shopee.vn/blog/cach-tra-hang-hoan-tien-tren-shopee/

### Khi Shopee yêu cầu bổ sung bằng chứng cho yêu cầu Trả hàng/Hoàn tiền, Người mua có bao nhiêu thời gian để phản hồi?
Thông thường là **24h** hoặc theo thời gian đếm ngược hiển thị trên ứng dụng. Nếu quá thời hạn này mà bạn không cung cấp đủ bằng chứng, Shopee có thể sẽ từ chối yêu cầu hoàn tiền của bạn.

### Shopee Xu và Mã giảm giá (Voucher) đã sử dụng sẽ được hoàn lại như thế nào khi yêu cầu Trả hàng/Hoàn tiền thành công?
Shopee Xu và Voucher sẽ được **tự động hoàn lại** vào tài khoản Người mua sau khi yêu cầu Trả hàng/Hoàn tiền được chấp nhận thành công, với điều kiện mã giảm giá vẫn còn hạn sử dụng tại thời điểm hoàn lại.

