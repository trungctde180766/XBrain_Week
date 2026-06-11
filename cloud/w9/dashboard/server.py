from flask import Flask, jsonify
from flask_cors import CORS
import subprocess, json, re

app = Flask(__name__)
CORS(app)

def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except:
        return ""

def kubectl(args):
    return run(f"kubectl {args}")

@app.route("/api/pods")
def pods():
    out = kubectl("get pods --all-namespaces -o json")
    try:
        data = json.loads(out)
        result = []
        for item in data.get("items", []):
            ns = item["metadata"]["namespace"]
            if ns in ["kube-system", "kube-node-lease", "kube-public"]:
                continue
            name = item["metadata"]["name"]
            phase = item["status"].get("phase", "Unknown")
            ready_containers = sum(
                1 for c in item["status"].get("containerStatuses", []) if c.get("ready")
            )
            total_containers = len(item["spec"].get("containers", []))
            restarts = sum(
                c.get("restartCount", 0) for c in item["status"].get("containerStatuses", [])
            )
            result.append({
                "namespace": ns,
                "name": name,
                "phase": phase,
                "ready": f"{ready_containers}/{total_containers}",
                "restarts": restarts,
            })
        return jsonify(result)
    except:
        return jsonify([])

@app.route("/api/apps")
def apps():
    out = kubectl("-n argocd get applications -o json")
    try:
        data = json.loads(out)
        result = []
        for item in data.get("items", []):
            name = item["metadata"]["name"]
            health = item["status"].get("health", {}).get("status", "Unknown")
            sync = item["status"].get("sync", {}).get("status", "Unknown")
            repo = item["spec"]["source"].get("repoURL", "")
            result.append({"name": name, "health": health, "sync": sync, "repo": repo})
        return jsonify(result)
    except:
        return jsonify([])

@app.route("/api/rollouts")
def rollouts():
    out = kubectl("-n demo get rollouts -o json 2>/dev/null")
    try:
        data = json.loads(out)
        result = []
        for item in data.get("items", []):
            name = item["metadata"]["name"]
            phase = item["status"].get("phase", "Unknown")
            desired = item["spec"].get("replicas", 0)
            ready = item["status"].get("readyReplicas", 0)
            result.append({"name": name, "phase": phase, "desired": desired, "ready": ready})
        return jsonify(result)
    except:
        return jsonify([])

@app.route("/api/nodes")
def nodes():
    out = kubectl("get nodes -o json")
    try:
        data = json.loads(out)
        result = []
        for item in data.get("items", []):
            name = item["metadata"]["name"]
            status = "Ready" if any(
                c["type"] == "Ready" and c["status"] == "True"
                for c in item["status"].get("conditions", [])
            ) else "NotReady"
            cpu = item["status"].get("capacity", {}).get("cpu", "?")
            mem = item["status"].get("capacity", {}).get("memory", "?")
            result.append({"name": name, "status": status, "cpu": cpu, "memory": mem})
        return jsonify(result)
    except:
        return jsonify([])

@app.route("/api/summary")
def summary():
    pods_out = kubectl("get pods --all-namespaces --no-headers")
    lines = [l for l in pods_out.splitlines() if l.strip()]
    running = sum(1 for l in lines if "Running" in l)
    total = len(lines)

    apps_out = kubectl("-n argocd get applications --no-headers")
    app_lines = [l for l in apps_out.splitlines() if l.strip()]
    synced = sum(1 for l in app_lines if "Synced" in l)

    nodes_out = kubectl("get nodes --no-headers")
    node_count = len([l for l in nodes_out.splitlines() if l.strip()])

    return jsonify({
        "pods_running": running,
        "pods_total": total,
        "apps_synced": synced,
        "apps_total": len(app_lines),
        "nodes": node_count,
    })

if __name__ == "__main__":
    print("🚀 Dashboard chạy tại http://localhost:9999")
    app.run(host="0.0.0.0", port=9999, debug=False)
