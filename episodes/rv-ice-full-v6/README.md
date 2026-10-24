# RV Ice Japanese — toàn tập v6, Muse chạy theo batch nhỏ

Kịch bản: **197 mục hình**, gồm 154 lần xuất hiện cảnh truyện, 23 khung thông tin và 20 thẻ ngày. Trong đó có **141 cảnh truyện cần tạo ảnh + video mới**. 13 lần xuất hiện cảnh demo dùng **12 bộ tài sản cũ riêng biệt**; không tạo lại chúng. Đã xuất sẵn đủ **43 PNG** của khung thông tin và thẻ ngày bằng Remotion.

Giọng toàn tập đã được tạo bằng OmniVoice speed 0.8 và căn theo audio thật tại máy chủ dự án local. Timeline có **38.545 frame / 30 fps**, khoảng **21 phút 24,8 giây**, gồm cả nhịp nghỉ và các khung thông tin. Muse chỉ tạo tài sản hình/video; không sửa lời Nhật, tạo lại voice, phụ đề, nhạc hoặc render tập cuối.

## Batch

- **24 batch**, tối đa **6 cảnh mới/batch**, một lượt generation hoạt động tại một thời điểm.
- Mỗi cảnh: ảnh có reference thật → kiểm tra ảnh → lưu và checkpoint → image-to-video 10 giây → tải file thật → giữ raw, tách tiếng bằng stream copy → kiểm tra → checkpoint.
- Batch sau chỉ cần common references, không phụ thuộc video của batch trước.
- Sau từng batch, trả các ZIP nhỏ độc lập và JSON trạng thái. Sau đó tiếp tục batch kế tiếp, không yêu cầu dán lại prompt.
- Giữ ảnh đã xong nếu video lỗi. Nếu một cảnh lỗi, đánh dấu riêng cảnh/stage đó, tiếp tục các cảnh độc lập.
- Nếu hết quota hoặc lỗi toàn tài khoản: dừng gọi tạo mới, lưu và xuất phần đã có, báo chính xác ID còn thiếu. Không mua credit, đổi gói, đổi tài khoản hay gọi API ngoài trả phí.

## Các tệp

| Tệp | Nội dung |
| --- | --- |
| `master-workflow.json` | Toàn bộ queue, phạm vi, giới hạn và hợp đồng output |
| `batches/B001.json` … `B024.json` | Prompt ảnh/video, timing thực, reference, continuity và đường dẫn output của từng batch |
| `image-prompts.full.json` | Ánh xạ tất cả mục hình sang generate/reuse/graphic |
| `video-prompts.full.json` | Prompt video và hành động tương ứng |
| `storyboard.full.json` | Timeline toàn tập, ID gốc và loại frame |
| `scripts/script.full.ja.md` | Kịch bản tiếng Nhật |
| `scripts/storyboard.full.ja.srt` | Ranh giới storyboard theo timing thực và các hold chủ ý |
| `scripts/timeline.full.csv` | Timeline để biên tập |
| `common/references.zip` | 6 ảnh tham chiếu thật; kiểm tra hash trước khi dùng |
| `common/graphics.zip` | 43 PNG đã dựng sẵn; không gửi image-to-video |
| `common/creative-bible.json` | Nhân vật, RV, phong cách, trạng thái tuyết và quy tắc chữ |
| `common/voice-timing.json` | SHA-256, duration và word alignment của 141 đoạn mới; WAV ở máy local |
| `common/reuse-existing.json` | Hash và vị trí các tài sản demo cũ trên máy Muse |
| `tools/bootstrap.py` | Tải đúng revision, xác minh và giải nén các input cần thiết |
| `tools/checkpoint.py` | Lưu tiến độ từng ảnh/clip, chống gửi generation trùng, kiểm tra file và xuất ZIP nhỏ |
| `tools/validate_package.py` | Kiểm tra cấu trúc package mà không gọi generation |

## Khởi chạy từ GitHub

Khóa mọi URL theo cùng một commit đầy đủ 40 ký tự. Tải `tools/bootstrap.py`, chạy:

```console
python bootstrap.py --base-url https://raw.githubusercontent.com/Standinwol/wf-stickman/COMMIT_SHA/episodes/rv-ice-full-v6/ --root workspace/rv-ice-full-v6
cd workspace/rv-ice-full-v6
python tools/validate_package.py
python tools/checkpoint.py init --batch batches/B001.json
python tools/checkpoint.py next --batch batches/B001.json
```

Sau `next`, dùng công cụ tạo ảnh/video tích hợp của Muse với prompt và file reference thật trong JSON. Helper chỉ quản lý file và trạng thái; không giả vờ đã tạo media và không thay thế image-to-video bằng code zoom ảnh.

Trước khi gọi generation, ghi `start`; sau khi tool trả `job_id`, lưu lại đúng ID đó. Nếu chưa biết kết quả của một lượt gọi, tìm/poll/download job cũ, không gửi thêm lượt tạo mới. Khi đã lưu output và đánh giá bằng công cụ xem ảnh/video, tạo QA JSON rồi ghi `record`:

```console
python tools/checkpoint.py start --batch batches/B001.json --scene full-001 --stage image --job-id ACTUAL_JOB_ID
python tools/checkpoint.py record --batch batches/B001.json --scene full-001 --stage image --file outputs/B001/images/full-001.png --qa outputs/B001/full-001-image-qa.json
python tools/checkpoint.py start --batch batches/B001.json --scene full-001 --stage video --job-id ACTUAL_JOB_ID
python tools/checkpoint.py record --batch batches/B001.json --scene full-001 --stage video --file outputs/B001/raw_videos/full-001.mp4 --qa outputs/B001/full-001-video-qa.json
python tools/checkpoint.py package --batch batches/B001.json
```

QA JSON tối thiểu: `{"ok":true,"observations":["mô tả những gì đã xem thực tế"],"warnings":[]}`. Không viết `ok:true` chỉ vì có prompt hoặc có thumbnail. Các cảnh `needs_review` vẫn phải được báo đúng và giữ file, không gọi lại toàn bộ batch.

Helper xác minh SHA-256 của file trước khi reuse. Nó giữ trạng thái `running` của job chưa rõ kết quả; lần `next` sau trả `resume_existing_job_only`, không tạo trùng. Mọi checkpoint được ghi atomic và có nhật ký JSONL. ZIP output là các archive độc lập, mục tiêu dưới 20 MB/part; không phải các volume cần nối byte.

## Chất lượng

Giữ một nhân vật chính sống một mình, RV kem sọc teal và hai tấm solar. Trạng thái tuyết và đồ đạc theo ngày có trong từng scene. Camera video đứng yên; chuyển động hành động/môi trường nhẹ, ngoại trừ các cảnh xe thực sự di chuyển. Không chữ, số hay logo sinh trong cảnh truyện. Giữ nguyên chữ Nhật trong 43 graphic có sẵn. Video có âm thanh phải được giữ raw và tạo bản silent riêng bằng stream copy.

Gói này là tài liệu và input đã hoàn tất, không phải tuyên bố 141 ảnh/video đã được Muse tạo. Trạng thái gửi/chạy thực được theo dõi ngoài manifest nguồn.
