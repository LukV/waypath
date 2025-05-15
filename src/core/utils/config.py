from enum import Enum

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

DEFAULT_PARSER = "llamaparse"
DEFAULT_MODEL = "openai"


class ObjectStatus(str, Enum):  # noqa: D101
    TO_ACCEPT = "to_accept"
    ACCEPTED = "accepted"
    ARCHIVED = "archived"
    DELETED = "deleted"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class ProcessingStatus(str, Enum):  # noqa: D101
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class ObjectType(str, Enum):  # noqa: D101
    ORDER = "order"
    INVOICE = "invoice"
    TENDER = "tender"
    TIMESHEET = "timesheet"


def setup_cors(app: FastAPI) -> None:
    """Set up CORS middleware for the FastAPI application."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8080", "https://www.waypath.be"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
