"""
Database Layer — SQLite access. No business logic here.
Only CRUD and schema management.
"""
import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "issues.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS issues (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                title       TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status      TEXT NOT NULL DEFAULT 'OPEN'
                            CHECK(status IN ('OPEN','IN_PROGRESS','DONE'))
            );
        """)


# ---------- Project queries ----------

def db_create_project(name: str) -> sqlite3.Row:
    with get_connection() as conn:
        cur = conn.execute("INSERT INTO projects (name) VALUES (?)", (name,))
        conn.commit()
        return conn.execute("SELECT * FROM projects WHERE id=?", (cur.lastrowid,)).fetchone()


def db_list_projects() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM projects ORDER BY id").fetchall()


def db_get_project(project_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()


# ---------- Issue queries ----------

def db_create_issue(project_id: int, title: str, description: str) -> sqlite3.Row:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO issues (project_id, title, description) VALUES (?,?,?)",
            (project_id, title, description),
        )
        conn.commit()
        return conn.execute("SELECT * FROM issues WHERE id=?", (cur.lastrowid,)).fetchone()


def db_list_issues(project_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM issues WHERE project_id=? ORDER BY id",
            (project_id,),
        ).fetchall()


def db_get_issue(issue_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM issues WHERE id=?", (issue_id,)).fetchone()


def db_update_issue_status(issue_id: int, new_status: str) -> sqlite3.Row:
    with get_connection() as conn:
        conn.execute(
            "UPDATE issues SET status=? WHERE id=?",
            (new_status, issue_id),
        )
        conn.commit()
        return conn.execute("SELECT * FROM issues WHERE id=?", (issue_id,)).fetchone()
