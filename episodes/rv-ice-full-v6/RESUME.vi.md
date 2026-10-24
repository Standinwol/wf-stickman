# Tiếp tục v6 với runner r2

Lỗi ở runner cũ: giới hạn một lần tạo/stage đã chặn cả lỗi thật không có output. Runner r2 cho phép tối đa một lần sửa riêng/stage, tổng tối đa 12 call sửa cho cả tập. Không cần xin phê duyệt lại cho các sửa này. Hết lượt sửa thì giữ needs_review/failed và báo đúng, không lặp vô hạn.

Giữ nguyên 24 batch bàn giao, tối đa 6 cảnh/batch. Mỗi lượt thực thi chỉ 2 scene ID, tối đa một work unit trong một tin nhắn. Đóng gói phần đã làm sau unit. Đây là cách giới hạn công việc; JSON không tự tạo được tin nhắn tiếp theo trên Muse. Chỉ dùng cơ chế tiếp tục nền nếu Muse thực sự hỗ trợ và trả task/job ID; nếu không thì báo rõ cần lượt nhắn tiếp. Không dùng cách lách quota, đổi tài khoản hoặc tự tạo lịch lặp.

## Cập nhật workspace đang chạy

Tải tools/update_runner.py từ commit r2 đã khóa trong tin giao việc, chạy với --base-url cùng commit và --root trỏ đúng workspace hiện có. Updater kiểm SHA-256 và fingerprint trước khi thay runner/manifest. Nó không chạm outputs/, deliveries/, state/, refs hoặc graphics. Không xóa checkpoint hay copy lại seed vào state/master-progress.json.

```console
python update_runner.py --base-url PINNED_RAW_BASE_URL --root EXISTING_WORKSPACE
cd EXISTING_WORKSPACE
python tools/dispatch.py next
```

Dispatcher ưu tiên job còn running, sau đó các cảnh first-pass đang thiếu, rồi mới danh sách sửa. Khi chụp trạng thái r2, điểm tiếp là B002/full-009/image, không phải B001/full-005. Luôn đọc checkpoint thật vì người dùng có thể đã tiếp tục trước đó.

## Retry riêng, giữ file cũ

Chỉ chạy retry khi job cũ đã lỗi terminal hoặc output có QA ok:false. Nếu còn pending/running/unknown thì lấy lại kết quả của đúng job cũ. Không retry tài sản đã đạt. full-001 được thử lại ảnh; full-002 và full-005 chỉ sửa video, dùng nguyên ảnh đã duyệt.

```console
python tools/checkpoint.py retry --batch batches/B001.json --scene full-001 --stage image --error "Confirmed terminal image error; no output saved"
python tools/checkpoint.py retry --batch batches/B001.json --scene full-002 --stage video --error "QA rejected camera drift and extra solar panels"
python tools/checkpoint.py next --batch batches/B001.json
```

Chỉ retry các ID nằm trong work unit sửa đang chọn. Dùng prompt và đường dẫn do next trả về: r02 cho file mới, metadata cũ nằm trong asset_history. Video repair có prompt chuyển động tối thiểu, khóa nguyên bố cục và không lộ vật ngoài khung. Mọi ảnh đã đạt giữ nguyên hash. Giữ video cũ cùng raw, silent, contact sheet để đối chiếu. Checkpoint/history và ZIP vẫn bàn giao cả file cũ và file sửa. Không đổi prompt fingerprint gốc để giả vờ đây là cảnh mới.

start vẫn phải ghi trước generation và cập nhật actual job_id ngay khi có. record chỉ đánh dấu ready sau khi xem output thật. Giới hạn theo tin nhắn: checkpoint và kết thúc unit; giới hạn quota toàn tài khoản: dừng tạo mới, báo lỗi thật. Hai trường hợp không giống nhau.
