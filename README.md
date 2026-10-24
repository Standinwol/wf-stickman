# RV Ice Japanese Demo — Muse workflow

**Gói toàn tập mới:** [RV Ice full v6 — 24 batch nhỏ](episodes/rv-ice-full-v6/README.md). Gồm kịch bản, prompt ảnh/video JSON, timing thực, 43 khung đồ họa đã xuất và công cụ checkpoint từng asset. Các tệp demo cũ bên dưới được giữ làm lịch sử và nguồn reuse.

Gói làm việc cho Muse web: **13 cảnh demo, timeline cuối 85,7 giây**.

- Dùng lại 13 ảnh đã chọn và clip 0001 đã tạo thành công.
- Tạo 12 clip image-to-video còn thiếu, mỗi clip nguồn 10 giây.
- Giữ script Nhật, 26 trang phụ đề và timeline 2571 frame / 30 fps.
- Dùng công cụ Muse và quota hiện tại; không mua credits, đổi gói hoặc dùng API ngoài trả phí.
- Dựng MP4 cuối bằng dự án Remotion local sau khi nhận asset. Gói này không yêu cầu làm tập 15–18 phút.

## Tệp đầu vào

| Tệp | Nội dung |
| --- | --- |
| [muse-rv-demo-workflow.json](./muse-rv-demo-workflow.json) | Workflow đầy đủ, 13 prompt ảnh, 13 prompt chuyển động, timing và quy tắc kiểm tra |
| [muse-rv-demo-inputs.zip](./muse-rv-demo-inputs.zip) | 13 ảnh, clip 0001 không tiếng và context đã khóa |
| [checksums.json](./checksums.json) | SHA-256 và kích thước hai tệp |

ZIP khoảng 35,7 MB được tải từ URL GitHub, không đi qua ô upload 25 MB của Muse.

## Giao việc cho Muse

Gửi nội dung [RUN-MUSE.vi.txt](./RUN-MUSE.vi.txt) vào một chat Muse.
Muse tải JSON và ZIP về máy của mình, kiểm tra SHA-256, giải nén ZIP, rồi chạy đủ các ID theo workflow.
Không cần dán từng prompt hoặc tải từng ảnh thủ công.

Đường dẫn tải trực tiếp:

- https://raw.githubusercontent.com/Standinwol/wf-stickman/main/muse-rv-demo-workflow.json
- https://raw.githubusercontent.com/Standinwol/wf-stickman/main/muse-rv-demo-inputs.zip
- https://raw.githubusercontent.com/Standinwol/wf-stickman/main/checksums.json

Khi gửi job thực tế, ưu tiên đường dẫn khóa theo commit để tất cả tệp cùng một revision.

## Kết quả cần nhận

Một ZIP `rv-ice-ja-demo-muse-assets-v1.zip`, có `images/`, `videos/`, `raw_videos/`,
`results.json`, `progress.json` và báo cáo kiểm tra bằng tiếng Việt. Muse phải báo đúng
các cảnh đã xong, lỗi, bị giới hạn hoặc còn chờ; lưu checkpoint sau từng ID.

Clip 0001 được giữ lại để tránh tạo lại: camera tiến vào mạnh hơn brief và kích thước
1248×704 gần 16:9. Workflow yêu cầu ghi rõ các điểm này. Clip mới dùng camera đứng yên.
Nếu công cụ vẫn tạo audio, giữ bản gốc và bỏ audio bằng stream copy trước khi bàn giao.

Các clip nguồn 10 giây sẽ được cắt theo timeline đã có; không kéo dài lời dẫn hoặc đổi tốc độ đọc.
