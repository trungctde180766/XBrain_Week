from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# In-memory store
todos = [
    {"id": 1, "title": "Deploy W9 GitOps", "done": True},
    {"id": 2, "title": "Setup ArgoCD", "done": True},
    {"id": 3, "title": "Configure Prometheus", "done": False},
]
next_id = 4

@app.route("/health")
def health():
    return jsonify(status="ok", version=os.getenv("VERSION", "v1"))

@app.route("/todos", methods=["GET"])
def get_todos():
    return jsonify(todos)

@app.route("/todos", methods=["POST"])
def create_todo():
    global next_id
    data = request.get_json()
    todo = {"id": next_id, "title": data["title"], "done": False}
    todos.append(todo)
    next_id += 1
    return jsonify(todo), 201

@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    for todo in todos:
        if todo["id"] == todo_id:
            todo["done"] = not todo["done"]
            return jsonify(todo)
    return jsonify(error="Not found"), 404

@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    global todos
    todos = [t for t in todos if t["id"] != todo_id]
    return jsonify(status="deleted")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
