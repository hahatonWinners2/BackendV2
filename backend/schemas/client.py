from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID


class ClientCreate(BaseModel):
    name: str = Field(..., max_length=100)
    address: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=500)

class MonthlyConsumptionCreate(BaseModel):
    client_id: UUID
    consumption: float

class MonthlyConsumptionCreate(BaseModel):
    client_id: UUID
    date: date
    consumption: float

    class Config:
        orm_mode = True

class MonthlyConsumptionResponse(BaseModel):
    date: date
    consumption: float

    class Config:
        orm_mode = True

