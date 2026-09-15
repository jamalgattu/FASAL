from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import MatchStatus


class MatchWeights(BaseModel):
    """Configurable weights for the matching engine. Must sum to 1.0 —
    the engine will normalize them if they don't, but a request with
    wildly unbalanced weights is still accepted (it's a legitimate way
    to say "distance barely matters to me")."""

    price: float = Field(default=0.25, ge=0, le=1)
    distance: float = Field(default=0.20, ge=0, le=1)
    quality: float = Field(default=0.20, ge=0, le=1)
    availability: float = Field(default=0.20, ge=0, le=1)
    reliability: float = Field(default=0.15, ge=0, le=1)


class MatchReasonSchema(BaseModel):
    label: str
    satisfied: bool


class MatchFactorScores(BaseModel):
    price_score: float
    distance_score: float
    quality_score: float
    availability_score: float
    reliability_score: float


class MatchAllocationRead(BaseModel):
    """One line of a proposed allocation — a single supplier's contribution
    toward fulfilling a requirement, with the full scoring breakdown."""

    listing_id: int
    farmer_id: int
    farmer_name: str
    allocated_quantity: float
    match_score: float
    distance_km: float
    factors: MatchFactorScores
    reasons: list[MatchReasonSchema]
    explanation: str


class MatchAllocationResponse(BaseModel):
    requirement_id: int
    requirement_remaining_quantity: float
    fully_allocated: bool
    allocations: list[MatchAllocationRead]


class MatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    listing_id: int
    requirement_id: int
    allocated_quantity: float
    match_score: float
    price_score: float
    distance_score: float
    quality_score: float
    availability_score: float
    reliability_score: float
    distance_km: float
    reasons: list[MatchReasonSchema]
    explanation: str
    status: MatchStatus
