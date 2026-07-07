import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI

# Load environment variables from a local .env file if present.
load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")

app = FastAPI(
    title="Task Tracker API",
    description=f"Module 1 Task Tracker REST API - skeleton project (env: {APP_ENV})",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """Basic liveness check for the API."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
