"""
FastAPI REST API server for GeneMindAI DNA sequence mutation analysis.

Exposes endpoints to health check the service and run real-time sequence prediction.
"""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, status

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.schemas import PredictionRequest, PredictionResponse
from backend.services.predictor import (
    InvalidDNASequenceError,
    Predictor,
    PredictorError,
)

# Global predictor instance initialized during application startup
predictor_service: Optional[Predictor] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager to load model once at startup."""
    global predictor_service
    try:
        predictor_service = Predictor()
    except Exception as exc:
        print(f"Error initializing predictor service: {exc}", file=sys.stderr)
        predictor_service = None
    yield
    predictor_service = None


app = FastAPI(
    title="GeneMindAI API",
    description="DNA Sequence Mutation Analysis & Beta Thalassemia Prediction API",
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

reports_dir = PROJECT_ROOT / "reports"
if reports_dir.is_dir():
    app.mount("/reports", StaticFiles(directory=reports_dir), name="reports")


@app.get("/", status_code=status.HTTP_200_OK)
async def root() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
        JSON response with API status message.
    """
    return {"message": "GeneMindAI API Running"}


@app.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
)
async def predict_dna_sequence(
    request: PredictionRequest,
) -> PredictionResponse:
    """
    Predict mutation status for a given DNA sequence.

    Args:
        request: PredictionRequest containing the DNA sequence.

    Returns:
        PredictionResponse containing classification label and confidence score.

    Raises:
        HTTPException 400: If the DNA sequence is invalid.
        HTTPException 500: If predictor is unavailable or inference fails.
    """
    if predictor_service is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Predictor service is not initialized.",
        )

    try:
        result_dict = predictor_service.predict(request.sequence)
        return PredictionResponse(**result_dict)
    except InvalidDNASequenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except PredictorError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
