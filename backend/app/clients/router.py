from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from datetime import date

from schemas.client import ClientCreate, MonthlyConsumptionCreate, MonthlyConsumptionResponse
from storage.models.client import Client
from storage.models.consumption import MonthlyConsumption
from storage.postgres import async_session
from datetime import date
from dateutil.relativedelta import relativedelta

def next_month(d: date) -> date:
    return d + relativedelta(months=1)



router = APIRouter()

@router.post("/clients/")
async def create_client(
    client_in: ClientCreate
):
    suspicion_level = 0

    new_client = Client(
        name=client_in.name,
        address=client_in.address,
        description=client_in.description,
        suspicion=suspicion_level,
        buildingType=client_in.buildingType,
        roomsCount=client_in.roomsCount,
        residentsCount=client_in.residentsCount,
    )

    async with async_session() as db:

        db.add(new_client)
        await db.commit()
        await db.refresh(new_client)

    return new_client


@router.post("/clients/{client_id}/monthly_consumption", response_model=MonthlyConsumptionCreate)
async def add_next_month_consumption(
    client_id: str,
    consumption_value: float
):
    
    async with async_session() as db:
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalars().first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

        result = await db.execute(
            select(MonthlyConsumption)
            .where(MonthlyConsumption.client_id == client_id)
            .order_by(MonthlyConsumption.date.desc())
            .limit(1)
        )
        last_consumption = result.scalars().first()

        if last_consumption:
            new_date = next_month(last_consumption.date)
        else:
            new_date = date.today().replace(day=1)

        new_consumption = MonthlyConsumption(
            client_id=client_id,
            date=new_date,
            consumption=consumption_value
        )

        db.add(new_consumption)
        await db.commit()
        await db.refresh(new_consumption)

    return new_consumption


@router.get("/clients/{client_id}/monthly_consumptions", response_model=list[MonthlyConsumptionResponse])
async def get_monthly_consumptions(
    client_id: str
):
    async with async_session() as db:
        # Check client exists
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalars().first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

        # Query monthly consumptions ordered by date
        result = await db.execute(
            select(MonthlyConsumption)
            .where(MonthlyConsumption.client_id == client_id)
            .order_by(MonthlyConsumption.date)
        )
        consumptions = result.scalars().all()

    return consumptions
