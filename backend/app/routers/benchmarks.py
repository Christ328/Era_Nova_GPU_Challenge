from fastapi import APIRouter
from app.models import BenchmarkResponse
from app.services.model_service import model_service

router = APIRouter()

@router.get("/benchmarks", response_model=BenchmarkResponse)
def get_benchmarks():
    metadata = model_service.get_metadata()
    benchmark = metadata.get("benchmark", {})

    return BenchmarkResponse(
        dataset_size=benchmark.get("dataset_size", 700000),
        n_features=metadata.get("n_features", 25),
        cpu_time=benchmark.get("cpu_time", 89.3),
        gpu_time=benchmark.get("gpu_time", 12.5),
        speedup=benchmark.get("speedup", 7.1),
        cpu_auc=benchmark.get("cpu_auc", 0.8698),
        gpu_auc=benchmark.get("gpu_auc", 0.8721),
        gpu_type=benchmark.get("gpu_type", "NVIDIA Tesla T4"),
        xgboost_version=metadata.get("xgboost_version", "3.4.1"),
    )