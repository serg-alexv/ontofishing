from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class Status(str, Enum):
    open = "open"
    rolling = "rolling"
    needs_verification = "needs_verification"
    closed = "closed"


class Effort(str, Enum):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"


class Opportunity(BaseModel):
    name: str
    official_url: HttpUrl
    domain: str
    status: Status = Status.needs_verification
    status_evidence: str = ""
    deadline: Optional[str] = None
    payout_amount: Optional[str] = None
    payout_numeric_usd_estimate: float = 0
    eligibility: str = ""
    deliverable: str = ""
    jurisdiction_or_payment_constraints: str = ""
    source_type: str = "official"
    effort: Effort = Effort.M
    domain_fit: float = Field(default=0.5, ge=0, le=1)
    verification_strength: float = Field(default=0.5, ge=0, le=1)
    payout_value: float = Field(default=0.5, ge=0, le=1)
    probability_of_success: float = Field(default=0.5, ge=0, le=1)
    portfolio_value: float = Field(default=0.5, ge=0, le=1)
    deadline_accessibility: float = Field(default=0.5, ge=0, le=1)
    low_admin_friction: float = Field(default=0.5, ge=0, le=1)
    eligibility_risk: float = Field(default=0.0, ge=0, le=1)
    payment_risk: float = Field(default=0.0, ge=0, le=1)
    stale_status_risk: float = Field(default=0.0, ge=0, le=1)
    competition_noise: float = Field(default=0.0, ge=0, le=1)
    notes: str = ""
