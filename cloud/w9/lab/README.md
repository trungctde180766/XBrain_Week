# W9 Lab: GitOps-ify + bolt-on observability + canary

## Mục tiêu
Nâng cấp cụm Kubernetes W8 để:
1. Quản lý toàn bộ cấu hình qua GitOps (ArgoCD).
2. Tích hợp công cụ theo dõi (Observability) tính toán SLO và cấu hình cảnh báo Burn rate.
3. Chuyển đổi deployment sang Rollout (Canary) kết hợp auto-abort khi metrics thấp.

## Các bước thực hiện
1. **Cài đặt ArgoCD** vào cluster W8.
2. Thiết lập **Application** trên ArgoCD trỏ về repo chứa manifest ứng dụng.
3. **Cài đặt OpenTelemetry Collector, Prometheus, Grafana, Loki**.
4. Cấu hình **PrometheusRule** cho SLO và cảnh báo burn rate multi-window.
5. Sửa đổi `Deployment` hiện tại thành `Rollout` và cấu hình strategy `canary`.
6. Định nghĩa `AnalysisTemplate` query Prometheus để quyết định canary tiến hay lùi.
7. Thử nghiệm **Load test** (bằng k6/vegeta) để quan sát auto-abort.
