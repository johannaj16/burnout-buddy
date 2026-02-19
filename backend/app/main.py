from fastapi import FastAPI

from app.api.v1.evening import router as evening_router
from app.db.init_db import init_db_schema

app = FastAPI(title="Burnout Buddy Backend", version="0.1.0")
app.include_router(evening_router, prefix="/v1")


@app.on_event("startup")
def startup() -> None:
    """Initialize local DB schema when Postgres is configured."""

    init_db_schema()
