from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health, merchants, assessments, benchmarks

app = FastAPI(
    title="GPU Credit Scoring API",
    description="API d'aide à la décision pour l'évaluation du risque de crédit des commerçants",
    version="1.0.0",
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

@app.get("/")
def root():
    return {"message": "GPU Credit Scoring API", "docs": "/docs", "version": "1.0.0"}