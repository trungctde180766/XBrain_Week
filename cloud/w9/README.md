# W9 Final Assignment: Automated Canary Release with GitOps & Observability

## Cấu trúc thư mục (Refactored)

Sau khi dọn dẹp các thư mục `day-a`, `day-b`, `day-c` lộn xộn, code hiện tại được refactor lại cực kỳ gọn gàng theo đúng chuẩn GitOps:

- `app/`: Chứa mã nguồn Flask API và Dockerfile dùng để build image (`w9-api:1`).
- `k8s-api/`: Chứa toàn bộ Kubernetes Manifests cho ứng dụng `api`.
  - `api.yaml`: Định nghĩa **Argo Rollout** (thay cho Deployment) với chiến lược Canary và **Service**.
  - `analysis-template.yaml`: Phân tích số liệu từ Prometheus để tự động quyết định promote (bản tốt -> 100%) hoặc abort (bản lỗi -> rollback) Canary.
  - `servicemonitor.yaml`: Cấu hình Prometheus cào (scrape) metrics `/metrics` từ API.
  - `slo-alert.yaml`: Cấu hình Alerting Rule cho SLO (thông báo khi Error Rate > 5%).
- `argocd/`: Chứa cấu trúc **App of Apps** cho ArgoCD.
  - `root.yaml`: Application gốc quản lý các apps bên trong.
  - `apps/api.yaml`: Quản lý ứng dụng api (trỏ về thư mục `k8s-api`).
  - `apps/argo-rollouts.yaml` & `apps/kube-prometheus-stack.yaml`: Cài đặt Argo Rollouts và Prometheus stack qua Helm.

## Giải thích Query & Ngưỡng (Threshold) cho Canary Analysis

Trong file `k8s-api/analysis-template.yaml`:

```yaml
  metrics:
  - name: success-rate
    interval: 10s
    count: 3
    successCondition: result[0] >= 0.90
    failureLimit: 1
    provider:
      prometheus:
        address: http://kube-prometheus-stack-prometheus.monitoring.svc.cluster.local:9090
        query: |
          sum(rate(flask_http_request_total{status!~"5.*", namespace="demo"}[1m])) 
          / 
          sum(rate(flask_http_request_total{namespace="demo"}[1m]))
```

**Giải thích Query:**
- `sum(rate(flask_http_request_total{status!~"5.*", namespace="demo"}[1m]))`: Tính tổng tốc độ request THÀNH CÔNG (các HTTP status KHÔNG bắt đầu bằng số 5 như 500, 502) trong 1 phút qua.
- `sum(rate(flask_http_request_total{namespace="demo"}[1m]))`: Tính tổng tốc độ CỦA TẤT CẢ request trong 1 phút qua.
- Phép chia này trả về **tỉ lệ thành công (Success Rate)** của API dưới dạng số thập phân từ 0 đến 1.

**Giải thích Ngưỡng (Threshold):**
- `successCondition: result[0] >= 0.90`: Yêu cầu tỉ lệ thành công tối thiểu phải đạt 90%. Nếu thấp hơn ngưỡng này, phân tích sẽ bị coi là failed.
- `count: 3` & `interval: 10s`: Đánh giá sẽ được lặp lại 3 lần, mỗi lần cách nhau 10 giây.
- `failureLimit: 1`: Chỉ cần 1 lần thất bại (Success Rate < 90%), toàn bộ quá trình Rollout sẽ lập tức tự động Abort và đưa API trở về phiên bản cũ an toàn.

## SLO & Alerting
- Trong `slo-alert.yaml`, alert `HighErrorRateAPI` được cấu hình để gửi cảnh báo khi tỉ lệ lỗi (Error Rate) vượt quá **5% trong 1 phút**.
- Khi inject lỗi (cập nhật VERSION với ERROR_RATE lớn) bằng cách commit qua Git, hệ thống sẽ trigger cảnh báo này tới Alertmanager (có thể cấu hình gửi Email/Slack) và AnalysisTemplate sẽ phát hiện lỗi để Rollout tự động rollback.
