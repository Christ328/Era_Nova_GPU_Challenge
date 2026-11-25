from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import IMFConfig  # registers the table with SQLAlchemy metadata
from app.routers import health, merchants, assessments, benchmarks, rules
from app.routers import imf
from app.routers.imf import seed_default_imf


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_default_imf(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="VIGIE-TRUST API",
    description="API d'aide à la décision VIGIE-TRUST",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.API_V1_PREFIX, tags=["health"])
app.include_router(merchants.router, prefix=settings.API_V1_PREFIX, tags=["merchants"])
app.include_router(assessments.router, prefix=settings.API_V1_PREFIX, tags=["assessments"])
app.include_router(benchmarks.router, prefix=settings.API_V1_PREFIX, tags=["benchmarks"])
app.include_router(rules.router, prefix=settings.API_V1_PREFIX, tags=["rules"])
app.include_router(imf.router, prefix=settings.API_V1_PREFIX, tags=["imf"])


@app.get("/")
def root():
    return {"message": "VIGIE-TRUST API", "docs": "/docs", "version": "1.0.0"}
