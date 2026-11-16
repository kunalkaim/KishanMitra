from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    phone_number: str = Field(..., json_schema_extra={"example": "9876543210"})
    full_name: str = Field(..., json_schema_extra={"example": "Surendra Singh Negi"})
    preferred_language: str = Field(default="hi", json_schema_extra={"example": "hi"})
    email: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, example="FarmerPassword123!")
    experience_years: Optional[int] = 5
    primary_irrigation_source: Optional[str] = "Canal / River"


class UserLogin(BaseModel):
    phone_number: str = Field(..., example="9876543210")
    password: str = Field(..., example="FarmerPassword123!")


class FarmerProfileOut(BaseModel):
    id: str
    experience_years: int
    primary_irrigation_source: Optional[str]
    has_kisan_credit_card: bool
    kcc_limit: float
    soil_health_card_number: Optional[str]
    annual_income_bracket: Optional[str]

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: str
    phone_number: str
    full_name: str
    email: Optional[str]
    preferred_language: str
    role: str
    is_active: bool
    is_verified: bool
    profile: Optional[FarmerProfileOut] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None
