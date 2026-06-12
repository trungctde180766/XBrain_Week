# W9 Reflection: Deliver Smartly

## Những gì đã học được
- **GitOps & CI/CD**: 
  - Hiểu rõ nguyên lý cốt lõi của GitOps (Git đóng vai trò là "Single Source of Truth"). Sử dụng ArgoCD để tự động hóa việc đồng bộ hóa các khai báo tài nguyên (manifest) từ kho lưu trữ GitHub lên cụm Kubernetes local (Minikube).
  - Tìm hiểu cách tổ chức mô hình App-of-Apps để quản lý tập trung nhiều ứng dụng con đồng thời.
  - Sử dụng cấu hình `Sync Waves` để kiểm soát chặt chẽ thứ tự khởi chạy tài nguyên trong cụm (đảm bảo `AnalysisTemplate` được tạo trước khi `Rollout` khởi chạy).
- **Observability**: 
  - Nắm vững khái niệm SLO (Service Level Objective) và SLI (Service Level Indicator) để định lượng chất lượng dịch vụ của hệ thống (trong lab là tỉ lệ thành công của API).
  - Sử dụng Prometheus để tự động cào metric thông qua `ServiceMonitor` và vẽ biểu đồ hiệu năng trực quan trên Grafana.
  - Thiết lập các quy tắc cảnh báo bằng `PrometheusRule` và tích hợp `AlertmanagerConfig` để tự động gửi email cảnh báo thông qua giao thức SMTP (Gmail App Password) về hòm thư cá nhân khi tỉ lệ lỗi hệ thống (HTTP 5xx) vượt quá 5% liên tục trong 1 phút.
- **Canary (Progressive Delivery)**: 
  - Hiểu và triển khai thành công chiến lược nâng cấp Canary Deployment bằng Argo Rollouts. Phân chia lưu lượng truy cập của người dùng theo các bước tăng dần (25% -> 50% -> 100%).
  - Sử dụng `AnalysisTemplate` chạy ngầm trong background để liên tục truy vấn Prometheus và tự động kích hoạt rollback tức thì (abort) về phiên bản an toàn trước đó nếu tỉ lệ thành công (Success Rate) tụt dưới 90%.

## Khó khăn gặp phải
- **Vấn đề độ trễ dữ liệu của Prometheus (Latency-bypass)**: 
  - *Mô tả:* Khi deploy bản lỗi v2, do cửa sổ tính toán PromQL rate quá dài (`[1m]`) trong khi thời gian kiểm tra quá ngắn (20s), dữ liệu lỗi mới chưa kịp kéo tỉ lệ thành công trung bình xuống dưới 90%, dẫn đến việc bản lỗi vượt qua phân tích thành công và trở thành bản stable.
  - *Cách giải quyết:* Rút ngắn cửa sổ rate trong PromQL từ `[1m]` xuống còn `[30s]` để tăng độ nhạy dữ liệu, đồng thời nâng số lần đánh giá của `AnalysisRun` lên 10 lần (quét liên tục trong 90s) để đảm bảo phát hiện lỗi kịp thời.
- **Lỗi deadlock do Poisoned Stable ReplicaSet**: 
  - *Mô tả:* Khi một phiên bản lỗi v2 vô tình lọt lưới lên làm bản stable (100% traffic lỗi), mọi bản deploy sửa lỗi tiếp theo đều bị rollback tự động vì 75% traffic của đợt deploy mới vẫn được định tuyến về bản stable lỗi này, kéo tỉ lệ thành công tổng thể đi xuống.
  - *Cách giải quyết:* Tạm thời tắt block `analysis` trong cấu hình để ép hệ thống nâng cấp một phiên bản v1 sạch lỗi lên làm stable (chiếm 100% traffic), sau khi dọn sạch hoàn toàn lỗi trong Prometheus mới bật lại block `analysis`.
- **Lỗi nghẽn Rollout không chạy đợt deploy mới**: 
  - *Mô tả:* Khi hệ thống ở trạng thái Aborted/Degraded, việc bấm nút "Fix & Restore" với thẻ tag phiên bản tĩnh (ví dụ `v1`) không làm thay đổi spec của YAML trên Git, khiến ArgoCD không nhận diện được thay đổi để kích hoạt đợt deploy mới.
  - *Cách giải quyết:* Thay đổi mã nguồn máy chủ dashboard để sinh tag phiên bản động có kèm theo dấu thời gian (`VERSION=v1-{timestamp}`) trong hàm sửa lỗi, đảm bảo ArgoCD luôn kích hoạt deploy đợt mới thành công.

## Bài học rút ra
- Trong mô hình GitOps, Git phải luôn là nguồn chân lý duy nhất. Hạn chế tối đa việc dùng `kubectl apply` tay trên cụm để tránh trôi lệch cấu hình (Configuration Drift).
- Hệ thống đo lường giám sát (Prometheus/Grafana) và hệ thống cảnh báo (Alertmanager) là thành phần sống còn để đội ngũ kỹ sư chủ động phát hiện sự cố trước khi người dùng phàn nàn.
- Khi cấu hình Progressive Delivery (Canary), các thông số thời gian cào metric (`scrape interval`) và cửa sổ tính toán (`rate window`) của Prometheus phải được thiết kế ăn khớp chặt chẽ với thời gian chờ (`pause duration`) của các bước Canary để cơ chế tự động hủy deploy hoạt động chính xác và nhạy bén.
