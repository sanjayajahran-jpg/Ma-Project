from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.car import CarDetailResponse


class CompareRequest(BaseModel):
    ids: Optional[List[int]] = Field(default=None, description="List of car IDs (2-4 items)")
    slugs: Optional[List[str]] = Field(default=None, description="List of car slugs (2-4 items)")


class CompareResponse(BaseModel):
    cars: List[CarDetailResponse]
