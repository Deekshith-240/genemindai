"""
Pydantic schemas for API request and response validation.
"""

from typing import Optional
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """DNA sequence prediction request payload."""

    sequence: str = Field(
        ...,
        description="Raw DNA nucleotide sequence string (A, T, C, G).",
        examples=["ACATTTGCTTCTGACACAACTGTGTTCACTAGCAACCTCAAACAGACACCATGGTGCAT"],
    )


class PredictionResponse(BaseModel):
    """DNA sequence prediction response payload."""

    prediction: str = Field(
        ...,
        description="Predicted sequence classification label (Healthy or Beta Thalassemia).",
        examples=["Healthy"],
    )
    confidence: float = Field(
        ...,
        description="Model prediction confidence score between 0.0 and 1.0.",
        examples=[0.71],
    )
    sequence_length: Optional[int] = Field(
        None,
        description="Sequence length in base pairs.",
        examples=[1606],
    )
    gc_content: Optional[float] = Field(
        None,
        description="GC content percentage.",
        examples=[52.3],
    )
    at_content: Optional[float] = Field(
        None,
        description="AT content percentage.",
        examples=[47.7],
    )
    model_used: Optional[str] = Field(
        "Random Forest",
        description="Machine learning model used for inference.",
        examples=["Random Forest"],
    )
    timestamp: Optional[str] = Field(
        None,
        description="Timestamp of prediction execution.",
        examples=["July 30, 2026 at 22:30:52"],
    )
