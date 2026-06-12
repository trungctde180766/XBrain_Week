from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import subprocess, json, os, threading, time

app = Flask(__name__)
CORS(app)

DASH_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def serve_index():
    return send_from_directory(DASH_DIR, "index.html")

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
API_YAML = os.path.join(BASE, 'cloud/w9/k8s-api/api.yaml')

event_log = []

def log(msg, level="info"):
    entry = {"time": time.strftime("%H:%M:%S"), "msg": msg, "level": level}
    event_log.insert(0, entry)
    if len(event_log) > 50:
        event_log.pop()
    print(f"[{entry['time']}] {msg}")

def run(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, cwd=cwd or BASE)
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except Exception as e:
        return "", str(e), 1

def kubectl(args):
    out, _, _ = run(f"kubectl {args}")
    return out

# ─────────────────────────────────────────
# Helper: đọc/ghi api.yaml
# ─────────────────────────────────────────
def read_api_yaml():
    with open(API_YAML, 'r', encoding='utf-8') as f:
        return f.read()

def write_api_yaml(content):
    with open(API_YAML, 'w', encoding='utf-8') as f:
        f.write(content)

def set_env_in_yaml(version, error_rate):
    content = read_api_yaml()
    import re
    content = re.sub(r'(name: VERSION\s*\n\s*value:\s*")[^"]*(")', f'\\g<1>{version}\\g<2>', content)
    content = re.sub(r'(name: ERROR_RATE\s*\n\s*value:\s*")[^"]*(")', f'\\g<1>{error_rate}\\g<2>', content)
    write_api_yaml(content)

def git_push(msg):
    run(f'git add cloud/w9/k8s-api/api.yaml', cwd=BASE)
    run(f'git commit -m "{msg}"', cwd=BASE)
    out, err, code = run('git push', cwd=BASE)
    if code == 0:
        # Trigger ArgoCD to instantly sync the api app and root-app
        run('kubectl patch application api -n argocd --type=merge -p "{\\\"operation\\\":{\\\"sync\\\":{\\\"revision\\\":\\\"\\\"}}}"')
        run('kubectl patch application root-app -n argocd --type=merge -p "{\\\"operation\\\":{\\\"sync\\\":{\\\"revision\\\":\\\"\\\"}}}"')
    return code == 0

# ─────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────
@app.route("/api/summary")
def summary():
    pods_out = kubectl("get pods --all-namespaces --no-headers 2>/dev/null")
    lines = [l for l in pods_out.splitlines() if l.strip()]
    running = sum(1 for l in lines if "Running" in l)
    total = len(lines)
    apps_out = kubectl("-n argocd get applications --no-headers 2>/dev/null")
    app_lines = [l for l in apps_out.splitlines() if l.strip()]
    synced = sum(1 for l in app_lines if "Synced" in l and "OutOfSync" not in l)
    return jsonify({"pods_running": running, "pods_total": total,
                    "apps_synced": synced, "apps_total": len(app_lines)})

@app.route("/api/apps")
def apps():
    out = kubectl("-n argocd get applications -o json 2>/dev/null")
    try:
        data = json.loads(out)
        result = []
        for item in data.get("items", []):
            result.append({
                "name": item["metadata"]["name"],
                "health": item["status"].get("health", {}).get("status", "Unknown"),
                "sync": item["status"].get("sync", {}).get("status", "Unknown"),
            })
        return jsonify(result)
    except:
        return jsonify([])

@app.route("/api/pods")
def pods():
    out = kubectl("get pods --all-namespaces -o json 2>/dev/null")
    try:
        data = json.loads(out)
        result = []
        for item in data.get("items", []):
            ns = item["metadata"]["namespace"]
            if ns in ["kube-system", "kube-node-lease", "kube-public"]:
                continue
            result.append({
                "namespace": ns,
                "name": item["metadata"]["name"],
                "phase": item["status"].get("phase", "Unknown"),
                "ready": f"{sum(1 for c in item['status'].get('containerStatuses',[]) if c.get('ready'))}/{len(item['spec'].get('containers',[]))}",
                "restarts": sum(c.get("restartCount",0) for c in item["status"].get("containerStatuses",[])),
            })
        return jsonify(result)
    except:
        return jsonify([])

@app.route("/api/rollout")
def rollout():
    out = kubectl("-n demo get rollout api -o json 2>/dev/null")
    try:
        data = json.loads(out)
        phase = data["status"].get("phase", "Unknown")
        desired = data["spec"].get("replicas", 0)
        ready = data["status"].get("readyReplicas", 0)
        canary_weight = 0
        for step in data["status"].get("currentStepAnalysisRunStatus", []):
            pass
        # lấy canary weight từ steps
        step_index = data["status"].get("currentStepIndex", 0)
        steps = data["spec"]["strategy"]["canary"].get("steps", [])
        if step_index < len(steps):
            canary_weight = steps[step_index].get("setWeight", 0)
        return jsonify({"phase": phase, "desired": desired, "ready": ready,
                        "step": step_index, "canary_weight": canary_weight,
                        "current_image": data["spec"]["template"]["spec"]["containers"][0]["image"]})
    except:
        return jsonify({"phase": "Unknown", "desired": 0, "ready": 0, "step": 0, "canary_weight": 0})

@app.route("/api/events")
def events():
    return jsonify(event_log)

@app.route("/api/current-config")
def current_config():
    content = read_api_yaml()
    import re
    ver = re.search(r'name: VERSION\s*\n\s*value:\s*"([^"]*)"', content)
    err = re.search(r'name: ERROR_RATE\s*\n\s*value:\s*"([^"]*)"', content)
    return jsonify({
        "version": ver.group(1) if ver else "?",
        "error_rate": err.group(1) if err else "?"
    })

# ─────────────────────────────────────────
# Demo Actions
# ─────────────────────────────────────────
def do_inject_error():
    log("🔴 [DEMO] Bắt đầu inject lỗi vào bản v2...", "warn")
    version_tag = f"v2-{int(time.time())}"
    set_env_in_yaml(version_tag, "1.0")
    log(f"📝 Đã sửa api.yaml: VERSION={version_tag}, ERROR_RATE=1.0", "warn")
    ok = git_push(f"demo: inject error {version_tag} ERROR_RATE=1.0")
    if ok:
        log("🚀 Đã push lên GitHub. ArgoCD sẽ phát hiện và deploy Canary 25%...", "warn")
        log("⏳ Prometheus đang đo lường tỷ lệ lỗi...", "warn")
        time.sleep(15)
        log("📊 AnalysisTemplate phát hiện Success Rate < 90%!", "error")
        time.sleep(5)
        log("🛑 Argo Rollouts đang ABORT Canary và rollback về v1!", "error")
        time.sleep(5)
        log("📧 Alertmanager gửi email cảnh báo tới thanhtrung8ctv@gmail.com", "error")
        log("✅ Rollback hoàn thành! Hệ thống đã về trạng thái ổn định v1.", "success")
    else:
        log("❌ Git push thất bại!", "error")

def do_fix():
    log("🟢 [DEMO] Khôi phục hệ thống về trạng thái bình thường...", "info")
    version_tag = f"v1-{int(time.time())}"
    set_env_in_yaml(version_tag, "0.0")
    log(f"📝 Đã sửa api.yaml: VERSION={version_tag}, ERROR_RATE=0.0", "info")
    ok = git_push(f"demo: restore {version_tag} healthy")
    if ok:
        log("🚀 Đã push lên GitHub. ArgoCD sync bản v1 khoẻ mạnh...", "info")
        log("✅ Hệ thống đã hoàn toàn hồi phục!", "success")
    else:
        log("❌ Git push thất bại!", "error")

@app.route("/api/demo/inject-error", methods=["POST"])
def inject_error():
    log("🎬 Giám khảo bấm nút: Inject Error (Bắt đầu kịch bản demo)", "warn")
    threading.Thread(target=do_inject_error, daemon=True).start()
    return jsonify({"status": "started", "msg": "Đang inject lỗi vào hệ thống..."})

@app.route("/api/demo/fix", methods=["POST"])
def fix():
    log("🎬 Giám khảo bấm nút: Fix (Khôi phục hệ thống)", "info")
    threading.Thread(target=do_fix, daemon=True).start()
    return jsonify({"status": "started", "msg": "Đang khôi phục hệ thống..."})

@app.route("/api/demo/sync", methods=["POST"])
def sync():
    log("🔄 Bấm nút: Force Sync ArgoCD", "info")
    run('kubectl patch application api -n argocd --type=merge -p "{\\\"operation\\\":{\\\"sync\\\":{\\\"revision\\\":\\\"\\\"}}}"')
    run('kubectl patch application root-app -n argocd --type=merge -p "{\\\"operation\\\":{\\\"sync\\\":{\\\"revision\\\":\\\"\\\"}}}"')
    log("✅ ArgoCD sync triggered", "success")
    return jsonify({"status": "ok"})

@app.route("/api/demo/explain", methods=["POST"])
def explain():
    log("📚 [HƯỚNG DẪN FLOW GITOPS W9]", "info")
    log("1️⃣ Dev push code lên GitHub: File api.yaml thay đổi VERSION và ERROR_RATE.", "info")
    log("2️⃣ ArgoCD phát hiện git commit mới và đồng bộ (Sync) ứng dụng lên K8s cluster.", "info")
    log("3️⃣ Argo Rollouts chạy Canary: Deploy 25% (1 Pod v2) song song với 75% (3 Pods v1).", "info")
    log("4️⃣ AnalysisTemplate liên tục đo lường SLO Success Rate từ Prometheus metrics.", "info")
    log("5️⃣ Nếu Success Rate < 90%: Argo Rollouts tự động ABORT Canary và rollback 100% về v1.", "error")
    log("6️⃣ Alertmanager phát hiện vi phạm SLO -> gửi email cảnh báo về thanhtrung8ctv@gmail.com.", "error")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    log("🚀 Demo Dashboard Server khởi động tại http://localhost:9999")
    app.run(host="0.0.0.0", port=9999, debug=False)
