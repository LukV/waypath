from dotenv import load_dotenv
from fastapi import FastAPI

from core.utils.config import setup_cors
from core.utils.database import Base, engine
from core.utils.logging import configure_logging

from .routers import auth, users

# Load environment variables
load_dotenv()

# Configure logging
configure_logging()

# Create FastAPI app instance
app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize configurations
setup_cors(app)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
