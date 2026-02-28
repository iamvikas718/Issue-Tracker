"""
Service Layer — Orchestrates domain rules + database.
API routes call this. Business rules live in domain.py, not here.
"""
from domain import IssueStatus, TransitionError, validate_transition
from database import (
    db_create_project, db_list_projects, db_get_project,
    db_create_issue, db_list_issues, db_get_issue, db_update_issue_status,
)


class NotFoundError(Exception):
    pass


class ValidationError(Exception):
    pass


# ---- helpers ----

def _row_to_dict(row) -> dict:
    return dict(row)


# ---- Project services ----

def svc_create_project(name: str) -> dict:
    name = (name or "").strip()
    if not name:
        raise ValidationError("Project name cannot be blank.")
    try:
        row = db_create_project(name)
    except Exception as e:
        if "UNIQUE" in str(e):
            raise ValidationError(f"A project named '{name}' already exists.")
        raise
    return _row_to_dict(row)


def svc_list_projects() -> list[dict]:
    return [_row_to_dict(r) for r in db_list_projects()]


def svc_get_project(project_id: int) -> dict:
    row = db_get_project(project_id)
    if not row:
        raise NotFoundError(f"Project {project_id} not found.")
    return _row_to_dict(row)


# ---- Issue services ----

def svc_create_issue(project_id: int, title: str, description: str = "") -> dict:
    title = (title or "").strip()
    if not title:
        raise ValidationError("Issue title cannot be blank.")
    # Ensure the project exists
    if not db_get_project(project_id):
        raise NotFoundError(f"Project {project_id} not found.")
    row = db_create_issue(project_id, title, description or "")
    return _row_to_dict(row)


def svc_list_issues(project_id: int) -> list[dict]:
    if not db_get_project(project_id):
        raise NotFoundError(f"Project {project_id} not found.")
    return [_row_to_dict(r) for r in db_list_issues(project_id)]


def svc_transition_issue(issue_id: int, new_status_str: str) -> dict:
    row = db_get_issue(issue_id)
    if not row:
        raise NotFoundError(f"Issue {issue_id} not found.")

    try:
        new_status = IssueStatus(new_status_str)
    except ValueError:
        valid = [s.value for s in IssueStatus]
        raise ValidationError(f"'{new_status_str}' is not a valid status. Choose from: {valid}.")

    current_status = IssueStatus(row["status"])
    validate_transition(current_status, new_status)  # raises TransitionError if blocked

    updated = db_update_issue_status(issue_id, new_status.value)
    return _row_to_dict(updated)
