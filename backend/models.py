from pydantic import BaseModel
from typing import List


class RoleMatch(BaseModel):
    """Model for role match with confidence"""
    role: str
    confidence: float


class PredictionResponse(BaseModel):
    """Response model for prediction endpoint"""
    candidate_name: str
    email: str
    phone: str
    education: str
    experience_years: int
    skills: str
    is_suitable: bool
    suitability_confidence: float
    recommended_role: str
    role_confidence: float
    top_3_roles: List[RoleMatch]
    recommendation: str
