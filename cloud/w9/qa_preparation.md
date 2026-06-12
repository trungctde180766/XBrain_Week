the# Hướng Dẫn Vấn Đáp Cảnh Báo SLO & Canary Deployment (Lab Tuần 9)

Tài liệu này tổng hợp các câu hỏi tiềm năng từ Mentor khi bảo vệ/vấn đáp bài Lab tuần 9, kèm theo các câu trả lời chuẩn xác nhất về mặt kỹ thuật để bạn chuẩn bị tốt nhất.

---

## PHẦN 1: CHIẾN LƯỢC CANARY & ARGO ROLLOUTS

### ❓ Câu 1: Làm sao Argo Rollouts biết được phiên bản mới (Canary) có lỗi để tự động rollback?
* **Trả lời:**
  Argo Rollouts giám sát chất lượng bản Canary thông qua **`AnalysisRun`** (được sinh ra từ `AnalysisTemplate`). Cứ mỗi 10 giây, nó sẽ gửi một truy vấn PromQL đến Prometheus để tính tỉ lệ thành công (Success Rate) của API. Nếu tỉ lệ thành công tụt dưới 90% (`successCondition: result[0] >= 0.90`), phân tích sẽ bị đánh dấu thất bại. Vì cấu hình `failureLimit: 1`, chỉ cần 1 lần thất bại duy nhất là Argo Rollouts lập tức hủy cập nhật (Abort) và đưa 100% traffic về bản chạy ổn định cũ.

### ❓ Câu 2: Sự khác nhau giữa Background Analysis và Inline Analysis Steps là gì?
* **Trả lời:**
  * **Background Analysis** (phân tích ngầm): Chạy liên tục song song trong suốt quá trình Rollout (từ bước 25% cho tới khi đạt 100%). Nếu lỗi xảy ra ở bất kỳ thời điểm nào, nó đều phát hiện và rollback ngay lập tức.
  * **Inline Analysis Steps**: Chỉ chạy kiểm tra tại một bước cụ thể được chỉ định sẵn (ví dụ: chuyển sang 25% rồi dừng lại chạy phân tích, phân tích xong mới đi tiếp). Nó không kiểm tra liên tục giữa các bước chuyển tiếp.

### ❓ Câu 3: Khi bản lỗi bị Rollback, trạng thái của Rollout trên ArgoCD hiển thị là gì và Pods của bản lỗi sẽ thế nào?
* **Trả lời:**
  Hệ thống sẽ chuyển sang trạng thái **`Degraded`** (trái tim nứt đỏ). Khi đó, Argo Rollouts lập tức chấm dứt (terminate) và xóa toàn bộ các Pod của bản lỗi về 0, đồng thời scale-up số Pod của bản cũ (stable) lên lại 100% (4 Pods) để đảm bảo không mất mát lưu lượng người dùng.

---

## PHẦN 2: PROMETHEUS & MONITORING

### ❓ Câu 4: Ý nghĩa của toán tử `by (namespace)` trong file cảnh báo `slo-alert.yaml` là gì?
* **Trả lời:**
  Mặc định, phép chia PromQL tính tỉ lệ lỗi sẽ lọc bỏ (strip) toàn bộ các nhãn nhạy cảm (như `namespace`). Việc dùng `by (namespace)` giúp **giữ lại nhãn `namespace="demo"`** sau phép tính. Nhãn này cực kỳ quan trọng để Alertmanager khớp điều kiện định tuyến và gửi mail cảnh báo, vì Alertmanager cấu hình của ta nằm ở namespace `demo`.

### ❓ Câu 5: Tại sao bạn lại chọn cửa sổ thời gian `[30s]` trong câu query của `AnalysisTemplate` thay vì `[1m]` hay `[5m]`?
* **Trả lời:**
  Sử dụng cửa sổ thời gian ngắn `[30s]` giúp Prometheus phản ứng rất nhạy với các lỗi mới phát sinh (khoảng 15-20s là chỉ số tụt ngay). Nếu dùng `[1m]` hoặc dài hơn, dữ liệu lỗi mới sẽ bị pha loãng bởi dữ liệu thành công của quá khứ, dẫn đến việc phân tích hoàn thành trước khi chỉ số kịp tụt dưới 90%, khiến bản lỗi có nguy cơ lọt lưới lên làm bản stable.

### ❓ Câu 6: `ServiceMonitor` đóng vai trò gì trong kiến trúc giám sát này?
* **Trả lời:**
  `ServiceMonitor` là tài nguyên của Prometheus Operator dùng để định nghĩa mục tiêu cào dữ liệu (scraping target). Nó chỉ định cho Prometheus biết cần gửi request vào đường dẫn nào (`/metrics`), cổng nào (`http`), tần suất bao lâu (`15s`) của Service `api` để thu thập số liệu.

---

## PHẦN 3: ALERTMANAGER & SMTP GỬI MAIL

### ❓ Câu 7: Làm sao Alertmanager biết được khi nào cần gửi mail và gửi vào hòm thư nào?
* **Trả lời:**
  Prometheus liên tục đánh giá luật cảnh báo (`PrometheusRule`). Khi luật bị vi phạm liên tục trong 1 phút, Prometheus đẩy cảnh báo sang Alertmanager. Alertmanager so khớp nhãn `severity: critical` và `namespace: demo`, sau đó định tuyến đến receiver `email-receiver` để gửi email tới địa chỉ Gmail được cấu hình qua giao thức SMTP (cổng 587).

### ❓ Câu 8: Bạn bảo mật thông tin mật khẩu gửi mail SMTP (Gmail App Password) trong Kubernetes bằng cách nào?
* **Trả lời:**
  Em lưu trữ App Password dưới dạng mã hóa Base64 trong một tài nguyên **`Kubernetes Secret`** tên là `email-smtp-secret`. Trong file `alertmanager-config.yaml`, em chỉ cần dùng `authPassword` tham chiếu (reference) đến Secret và Key đó chứ không bao giờ hardcode mật khẩu dạng văn bản thô.

---

## PHẦN 4: CÂU HỎI TÌNH HUỐNG/THỰC TẾ (CỰC KỲ DỄ BỊ HỎI)

### ❓ Câu 9: Trong quá trình làm, bạn có gặp tình trạng bản lỗi `v2` vô tình bị đẩy lên làm stable và khóa chết hệ thống không? Bạn xử lý thế nào?
* **Trả lời:**
  Dạ có. Đó là lỗi **Poisoned Stable ReplicaSet**. Khi bản lỗi bị promote thành bản stable, nó chạy ở 100% traffic và tạo ra 100% lỗi. Bất kỳ đợt deploy sửa lỗi sau đó đều bị rollback ngược về bản lỗi này do Prometheus đo được tỉ lệ lỗi tổng thể trong cụm quá cao.

  **Cách xử lý:** Em tạm thời gỡ bỏ cấu hình `analysis` khỏi file `api.yaml` để tắt kiểm tra tự động, ép hệ thống cập nhật lên phiên bản sạch lỗi lên 100% stable. Sau khi hệ thống đã ổn định và hết sạch lỗi trong Prometheus, em bật lại block `analysis` để khôi phục cơ chế bảo vệ.
