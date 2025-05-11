from enum import Enum

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class OrderStatus(str, Enum):  # noqa: D101
    PROCESSING = "processing"
    TO_ACCEPT = "to_accept"
    ACCEPTED = "accepted"
    ARCHIVED = "archived"
    DELETED = "deleted"
    FAILED = "failed"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


def setup_cors(app: FastAPI) -> None:
    """Set up CORS middleware for the FastAPI application."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
