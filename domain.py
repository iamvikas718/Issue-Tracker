"""
Domain Layer — Pure business rules, no Flask, no SQLite.
This is the source of truth for what is allowed.
"""
from enum import Enum


class IssueStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


# The ONLY valid transitions. Period.
VALID_TRANSITIONS: dict[IssueStatus, set[IssueStatus]] = {
    IssueStatus.OPEN: {IssueStatus.IN_PROGRESS},
    IssueStatus.IN_PROGRESS: {IssueStatus.DONE},
    IssueStatus.DONE: set(),  # Terminal state
}


class TransitionError(Exception):
    """Raised when a status transition is not allowed."""
    pass


def validate_transition(current: IssueStatus, next_status: IssueStatus) -> None:
    """
    Enforce the state machine. Raises TransitionError if invalid.
    This is called by the service layer — never bypassed.
    """
    allowed = VALID_TRANSITIONS.get(current, set())
    if next_status not in allowed:
        raise TransitionError(
            f"Cannot transition from {current.value} to {next_status.value}. "
            f"Allowed: {[s.value for s in allowed] or 'none (terminal state)'}."
        )
