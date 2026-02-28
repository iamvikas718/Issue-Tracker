"""
API Layer — Flask routes. Thin. No business logic.
Translates HTTP → service calls → HTTP responses.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS

from database import init_db
from services import (
    svc_create_project, svc_list_projects, svc_get_project,
    svc_create_issue, svc_list_issues, svc_transition_issue,
    NotFoundError, ValidationError,
)
from domain import TransitionError

app = Flask(__name__)
CORS(app, origins=[
    "https://iamvikas718.github.io",
    "http://localhost:8080",
    "http://127.0.0.1:5500"
])
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({"ok": True})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        return response
# ── Error helpers ──────────────────────────────────────────────────────────────

def ok(data, status=200):
    return jsonify({"ok": True, "data": data}), status


def err(message, status=400):
    return jsonify({"ok": False, "error": message}), status


# ── Projects ───────────────────────────────────────────────────────────────────

@app.route("/api/projects", methods=["GET"])
def list_projects():
    return ok(svc_list_projects())


@app.route("/api/projects", methods=["POST"])
def create_project():
    body = request.get_json(silent=True) or {}
    try:
        project = svc_create_project(body.get("name", ""))
    except ValidationError as e:
        return err(str(e))
    return ok(project, 201)


@app.route("/api/projects/<int:project_id>", methods=["GET"])
def get_project(project_id):
    try:
        return ok(svc_get_project(project_id))
    except NotFoundError as e:
        return err(str(e), 404)


# ── Issues ─────────────────────────────────────────────────────────────────────

@app.route("/api/projects/<int:project_id>/issues", methods=["GET"])
def list_issues(project_id):
    try:
        return ok(svc_list_issues(project_id))
    except NotFoundError as e:
        return err(str(e), 404)


@app.route("/api/projects/<int:project_id>/issues", methods=["POST"])
def create_issue(project_id):
    body = request.get_json(silent=True) or {}
    try:
        issue = svc_create_issue(
            project_id,
            title=body.get("title", ""),
            description=body.get("description", ""),
        )
    except NotFoundError as e:
        return err(str(e), 404)
    except ValidationError as e:
        return err(str(e))
    return ok(issue, 201)


@app.route("/api/issues/<int:issue_id>/transition", methods=["POST"])
def transition_issue(issue_id):
    body = request.get_json(silent=True) or {}
    new_status = body.get("status", "")
    try:
        issue = svc_transition_issue(issue_id, new_status)
    except NotFoundError as e:
        return err(str(e), 404)
    except (ValidationError, TransitionError) as e:
        return err(str(e), 422)
    return ok(issue)


# ── Startup ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
