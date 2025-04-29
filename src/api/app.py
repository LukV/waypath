from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from core.utils.config import setup_cors
from core.utils.database import Base, engine
from core.utils.logging import configure_logging

from .routers import auth, users

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    """Lifespan event handler."""
    # Startup: create tables (only for local dev)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: (if needed later) : await cleanup()


# Create FastAPI app instance
app = FastAPI(lifespan=lifespan)

# Load configs
configure_logging()
setup_cors(app)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
