# Hướng Dẫn Vấn Đáp Cảnh Báo SLO & Canary Deployment (Lab Tuần 9)

Tài liệu này tổng hợp các câu hỏi tiềm năng từ Mentor khi bảo vệ/vấn đáp bài Lab tuần 9, kèm theo các câu trả lời chuẩn xác nhất về mặt kỹ thuật để bạn chuẩn bị tốt nhất.

---

## PHẦN 1: CHIẾN LƯỢC CANARY & ARGO ROLLOUTS

### ❓ Câu 1: Làm sao Argo Rollouts biết được phiên bản mới (Canary) có lỗi để tự động rollback?
* **Trả lời:**
  Argo Rollouts giám sát chất lượng bản Canary thông qua **`AnalysisRun`** (được sinh ra từ `AnalysisTemplate`). Cấu hình cụ thể trong file `analysis-template.yaml` của chúng ta như sau:

  ```yaml
    metrics:
    - name: success-rate
      interval: 10s
      count: 10
      successCondition: result[0] >= 0.90
      failureLimit: 1
      provider:
        prometheus:
          address: http://kube-prometheus-stack-prometheus.monitoring.svc.cluster.local:9090
          query: |
            sum(rate(flask_http_request_total{status!~"5.*", namespace="demo"}[30s])) 
            / 
            sum(rate(flask_http_request_total{namespace="demo"}[30s]))
  ```

  **Cơ chế hoạt động:**
  1. Cứ mỗi **10 giây (`interval: 10s`)**, Argo Rollouts sẽ tự động gửi câu truy vấn PromQL ở trên đến Prometheus để tính toán tỉ lệ thành công.
  2. **Công thức tính Tỉ lệ thành công (Success Rate):**
     $$\text{Success Rate} = \frac{\text{Tổng request THÀNH CÔNG (HTTP Status không bắt đầu bằng số 5)}}{\text{Tổng TẤT CẢ request gửi đến hệ thống}}$$
     * *Ví dụ:* Nếu hệ thống có tổng cộng 100 request, trong đó có 5 request bị lỗi 500 (chỉ có 95 request thành công), tỉ lệ thành công sẽ là $\frac{95}{100} = 0.95$ (tương đương 95%).
  3. **Điều kiện đánh giá:**
     * **`successCondition: result[0] >= 0.90`**: Kết quả tính toán phải đạt tối thiểu **90%** (tức là $\ge 0.90$). Nếu kết quả trả về nhỏ hơn 0.90 (dưới 90%), lượt kiểm tra đó bị coi là thất bại (`Failed`).
     * **`failureLimit: 1`**: Chỉ cần **1 lần duy nhất** có kết quả dưới 90%, Argo Rollouts sẽ lập tức Abort (Hủy cập nhật) và tự động kéo toàn bộ 100% traffic trở về bản cũ an toàn.


### ❓ Câu 1b: `AnalysisTemplate` là gì? Phân biệt nó với `AnalysisRun` như thế nào?
* **Trả lời:**
  * **`AnalysisTemplate` (Mẫu phân tích):** Là bản thiết kế/công thức định nghĩa sẵn. Nó quy định: *lấy metrics gì (ví dụ: success-rate), lấy từ đâu (địa chỉ Prometheus), tần suất bao lâu (10s), và ngưỡng thế nào là đạt (>= 90%)*. Cấu hình này tĩnh, khai báo sẵn và tự nó không hoạt động.
  * **`AnalysisRun` (Lượt thực thi phân tích):** Là **thực thể sống (instance)** được tạo ra chạy thực tế. Khi Argo Rollouts thực hiện deploy bản Canary, nó sẽ dựa vào `AnalysisTemplate` để sinh ra một `AnalysisRun` tương ứng để chạy tính toán real-time ngoài cụm và ra quyết định thành công hay thất bại.


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

## PHẦN 4: CƠ CHẾ GITOPS & ARGOCD ARCHITECTURE

### ❓ Câu 9: GitOps là gì? Tại sao lại dùng GitOps thay vì deploy bằng `kubectl apply` thủ công?
* **Trả lời:**
  * **GitOps** là phương pháp vận hành hệ thống trong đó Git đóng vai trò là "Single Source of Truth" (Nguồn chân lý duy nhất). Mọi trạng thái mong muốn của hệ thống đều được khai báo dưới dạng code trong Git.
  * **Lợi ích:** Dễ dàng kiểm soát lịch sử thay đổi (Audit log), phân quyền qua Pull Request, tự động đồng bộ (Self-healing) khi có sự thay đổi sai lệch ngoài cụm, và dễ dàng khôi phục (Rollback/Disaster Recovery) hệ thống về trạng thái cũ chỉ bằng 1 lệnh `git revert`.

### ❓ Câu 10: Khái niệm "drift" (sai lệch cấu hình) trong GitOps là gì và ArgoCD xử lý nó thế nào?
* **Trả lời:**
  * **Drift** xảy ra khi ai đó cố tình dùng lệnh `kubectl edit` hoặc `kubectl apply` trực tiếp trên cụm K8s làm thay đổi tài nguyên ngoài cụm so với file cấu hình gốc trên Git.
  * **Cách xử lý:** ArgoCD liên tục đối chiếu trạng thái thực tế ngoài cụm với file cấu hình trên Git. Nếu phát hiện sai lệch, ArgoCD sẽ đánh dấu trạng thái ứng dụng là `OutOfSync`. Nếu bật tính năng `Self-Healing`, ArgoCD sẽ tự động ghi đè cấu hình ngoài cụm về đúng cấu hình trên Git.

### ❓ Câu 11: Mô hình "App of Apps" trong ArgoCD là gì? Tại sao lại cần dùng nó?
* **Trả lời:**
  * **App of Apps** là mô hình quản lý nơi ta tạo ra một Application ArgoCD cha, và Application này trỏ tới một thư mục trên Git chứa các file YAML của các Application ArgoCD con (như kube-prometheus-stack, argo-rollouts, api...).
  * **Lợi ích:** Giúp quản lý toàn bộ các ứng dụng trong cụm từ một nơi duy nhất. Khi cần cài mới hoặc gỡ bỏ một ứng dụng, ta chỉ cần thay đổi file cấu hình ứng dụng con trên Git, ArgoCD sẽ tự động cài/gỡ ứng dụng đó trên K8s mà không cần can thiệp thủ công.

### ❓ Câu 12: `Sync Waves` trong ArgoCD hoạt động như thế nào? Tại sao lại đặt `sync-wave: "-1"` cho AnalysisTemplate?
* **Trả lời:**
  * **Sync Waves** cho phép thiết lập thứ tự cài đặt các tài nguyên trong ArgoCD (nhóm nào chạy trước, nhóm nào chạy sau). Wave có số nhỏ hơn sẽ được deploy trước.
  * **Giải thích:** Việc đặt `sync-wave: "-1"` cho `AnalysisTemplate` đảm bảo rằng mẫu phân tích chất lượng phải được cài đặt thành công vào K8s **trước** khi đối tượng `Rollout` của ứng dụng chạy (mặc định các tài nguyên khác có wave là `0`). Nếu Rollout chạy trước khi có AnalysisTemplate, Rollout sẽ bị lỗi vì không tìm thấy mẫu đánh giá.

---

## PHẦN 5: CÂU HỎI KỸ THUẬT SÂU & THỰC TẾ

### ❓ Câu 13: Trong quá trình làm, bạn có gặp tình trạng bản lỗi `v2` vô tình bị đẩy lên làm stable và khóa chết hệ thống không? Bạn xử lý thế nào?
* **Trả lời:**
  Dạ có. Đó là lỗi **Poisoned Stable ReplicaSet**. Khi bản lỗi bị promote thành bản stable, nó chạy ở 100% traffic và tạo ra 100% lỗi. Bất kỳ đợt deploy sửa lỗi sau đó đều bị rollback ngược về bản lỗi này do Prometheus đo được tỉ lệ lỗi tổng thể trong cụm quá cao.

  **Cách xử lý:** Em tạm thời gỡ bỏ cấu hình `analysis` khỏi file `api.yaml` để tắt kiểm tra tự động, ép hệ thống cập nhật lên phiên bản sạch lỗi lên 100% stable. Sau khi hệ thống đã ổn định và hết sạch lỗi trong Prometheus, em bật lại block `analysis` để khôi phục cơ chế bảo vệ.

### ❓ Câu 14: Tại sao cần `readinessProbe` trong Pod template? Nếu thiếu nó, Canary deployment sẽ ra sao?
* **Trả lời:**
  * **`readinessProbe`** (kiểm tra mức độ sẵn sàng) giúp Kubernetes biết khi nào container khởi động xong hoàn toàn và sẵn sàng tiếp nhận traffic của khách hàng.
  * **Hậu quả nếu thiếu:** K8s sẽ lập tức gửi traffic vào container ngay khi nó vừa được tạo. Nếu ứng dụng mất 5-10 giây để khởi động (load thư viện, kết nối DB), khách hàng sẽ nhận ngay lỗi `502/503` trong khoảng thời gian khởi động này, trực tiếp làm tụt SLO và kích hoạt Rollback lỗi.

### ❓ Câu 15: Làm sao để debug khi Alertmanager không gửi được email cảnh báo về Gmail?
* **Trả lời:**
  Em sẽ thực hiện debug theo 4 bước sau:
  1. Kiểm tra trạng thái Alert trên trang Prometheus UI xem alert đã chuyển sang màu đỏ (`Firing`) hay chưa.
  2. Xem logs của Pod Alertmanager bằng lệnh `kubectl logs -n monitoring alertmanager-kube-prometheus-stack-alertmanager-0` để tìm các dòng báo lỗi SMTP (ví dụ: lỗi xác thực tài khoản, lỗi kết nối mạng...).
  3. Kiểm tra xem Secret `email-smtp-secret` đã có thông tin chính xác hay chưa.
  4. Đảm bảo Gmail đã bật mật khẩu ứng dụng (App Password) và máy chủ Minikube có kết nối Internet để kết nối tới `smtp.gmail.com:587`.

### ❓ Câu 16: Tần suất cào dữ liệu (`scrape interval`) của Prometheus ảnh hưởng thế nào đến độ nhạy của Canary Analysis?
* **Trả lời:**
  * Tần suất cào dữ liệu quyết định tốc độ Prometheus cập nhật số liệu mới từ API. Trong bài lab, ta đặt `interval: 15s` trong `ServiceMonitor`.
  * Nếu đặt scrape interval quá dài (ví dụ: `1m` hoặc `5m`), Prometheus sẽ mất rất nhiều thời gian để ghi nhận lỗi mới. Việc này khiến các công cụ giám sát như Argo Rollouts bị mù thông tin tạm thời và có thể vô tình cho qua bản lỗi vì chỉ số thành công trong database Prometheus chưa kịp thay đổi.

### ❓ Câu 17: Làm sao bạn tạo ra lượng traffic giả lập để Prometheus đo đạc chỉ số?
* **Trả lời:**
  Em chạy một Pod giả lập traffic tên là **`traffic-generator`** trong namespace `demo`. Pod này chạy một vòng lặp vô hạn sử dụng lệnh `wget` liên tục gửi các HTTP request lên Service `api` với tần suất khoảng 10-20 request mỗi giây, đảm bảo luôn có dữ liệu real-time chạy trong cụm.

### ❓ Câu 18: Sự kết hợp giữa Service type `ClusterIP` và `LoadBalancer` là gì? Service của API đang dùng loại nào?
* **Trả lời:**
  * **`ClusterIP`** (loại mặc định, Service `api` đang dùng): Chỉ cấp một IP nội bộ bên trong cụm K8s. Các dịch vụ bên ngoài cụm không thể kết nối trực tiếp đến IP này.
  * **`LoadBalancer`**: Tự động tích hợp và cấp một IP công cộng bên ngoài (External IP) thông qua đám mây (AWS, GCP) hoặc bộ định tuyến ảo (Metallb) để người dùng từ Internet truy cập trực tiếp vào ứng dụng.

---

## PHẦN 6: DÒ BÀI DÒNG CODE CHI TIẾT (LINE-BY-LINE DEFENSE)

### ❓ Câu 19: Trong `servicemonitor.yaml`, dòng `release: kube-prometheus-stack` ở mục labels dùng để làm gì?
* **Trả lời:**
  * Dòng này đính kèm nhãn (label) định danh của bộ Helm release Prometheus Stack. Prometheus Operator được cấu hình để chỉ quét và tự động nạp cấu hình cào metric từ các `ServiceMonitor` nào có nhãn `release` khớp với tên Helm release đang chạy. Nếu xóa hoặc sửa dòng này thành tên khác, Prometheus Server sẽ bỏ qua file này và không cào metrics của Flask API.

### ❓ Câu 20: Trong `api.yaml`, dòng `startingStep: 1` dùng để làm gì?
* **Trả lời:**
  * Dòng này cấu hình thời điểm bắt đầu chạy `AnalysisRun` (phân tích ngầm). Số `1` đại diện cho index của bước trong mảng `steps` (bước 1 là index 0: `setWeight: 25`, bước 2 là index 1: `pause: 30s`). `startingStep: 1` nghĩa là hệ thống sẽ đợi cho đến khi bước đầu tiên (25% traffic) được áp dụng xong rồi mới kích hoạt chạy phân tích lỗi ở nền, tránh việc đo đạc khi chưa có lưu lượng nào đổ vào bản mới.

### ❓ Câu 21: Trong `analysis-template.yaml`, dòng `failureLimit: 1` dùng để làm gì?
* **Trả lời:**
  * Dòng này đặt số lần thất bại tối đa cho phép của đợt phân tích. Với giá trị là `1`, chỉ cần Prometheus trả về kết quả kiểm tra Success Rate nhỏ hơn 90% đúng **1 lần duy nhất**, đợt deploy sẽ bị coi là lỗi, Argo Rollouts lập tức dừng deploy (abort) và rollback về bản cũ để bảo vệ người dùng.

### ❓ Câu 22: Trong `slo-alert.yaml`, dòng `for: 1m` dùng để làm gì?
* **Trả lời:**
  * Dòng này chỉ định thời gian trì hoãn trước khi phát cảnh báo chính thức (`Firing`). Tỉ lệ lỗi phải vượt quá 5% liên tục trong vòng 1 phút thì Prometheus mới phát alert khẩn cấp. Dòng này giúp lọc bớt các báo động giả khi hệ thống chỉ bị nghẽn mạng hoặc lỗi tạm thời trong vài giây.

### ❓ Câu 23: Trong `alertmanager-config.yaml`, dòng `groupBy: ['alertname']` dùng để làm gì?
* **Trả lời:**
  * Dòng này gom nhóm các cảnh báo theo tên cảnh báo. Nếu hệ thống đồng loạt phát sinh nhiều alert cùng tên (ví dụ nhiều Pod cùng báo `HighErrorRateAPI` cùng lúc), Alertmanager sẽ gom tất cả chúng lại để gửi đi trong một email duy nhất thay vì spam hộp thư của người dùng bằng hàng chục email riêng lẻ.

### ❓ Câu 24: Trong `api.yaml`, dòng `imagePullPolicy: IfNotPresent` dùng để làm gì?
* **Trả lời:**
  * Dòng này quy định chính sách tải image của container. K8s sẽ ưu tiên sử dụng bản image có sẵn ở bộ nhớ node local trước; nếu không tìm thấy mới tải từ registry về. Dòng này giúp tối ưu hóa thời gian deploy và tránh quá tải mạng khi chạy local trên Minikube.

### ❓ Câu 25: Trong `slo-alert.yaml`, dòng `status=~"5.*"` dùng để làm gì?
* **Trả lời:**
  * Đây là cú pháp sử dụng biểu thức chính quy (regular expression) trong PromQL. Dấu `=~` là so khớp regex, `"5.*"` đại diện cho tất cả các HTTP status code bắt đầu bằng số 5 (như 500, 502, 503, 504), giúp Prometheus lọc ra chính xác các lỗi phát sinh từ phía server.

### ❓ Câu 26: Trong `alertmanager-config.yaml`, dòng `smarthost: 'smtp.gmail.com:587'` dùng để làm gì?
* **Trả lời:**
  * Dòng này chỉ định địa chỉ máy chủ SMTP và cổng kết nối của Google Gmail. Cổng `587` là cổng chuẩn sử dụng giao thức bảo mật STARTTLS để mã hóa đường truyền thư trước khi gửi, đảm bảo thông tin đăng nhập tài khoản và nội dung email được truyền đi an toàn.
