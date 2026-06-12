from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_tables
from app.routers import manuscripts, analysis, metadata, marketing, export

app = FastAPI(title="Publishing OS", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(manuscripts.router)
app.include_router(analysis.router)
app.include_router(metadata.router)
app.include_router(marketing.router)
app.include_router(export.router)


@app.on_event("startup")
def on_startup() -> None:
    create_db_tables()


@app.get("/health")
def health() -> dict:
    return {"status": "healthy"}
