from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import FileResponse
import json
import tempfile
from pydantic import BaseModel

from utils.algorithm.processor import get_answers
from utils.claim_generation.main import generate_pdf


class CourtData(BaseModel):
    court_name: str
    court_address: str
    istec: str
    istec_inn: str
    istec_ogrn: str
    istec_address: str
    otvetchik_name: str
    otvetchik_address: str
    damage_sum: str
    consumption_period: str
    activity_type: str
    act_date: str
    expertise_date: str
    tariff_calculation: str


router = APIRouter()


@router.post("/upload-json/")
async def upload_json(file: UploadFile):
    if file.content_type != "application/json":
        raise HTTPException(status_code=400, detail="Invalid file type. JSON required.")
    content = await file.read()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file.")
    
    answers = get_answers(data)

    return [{'accountId': d['accountId'], 'isCommercial': answers[i], 'address': d['address']} for i, d in enumerate(data)]


@router.post("/get_claim")
async def create_pdf(data: CourtData):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        generate_pdf(data.model_dump(), tmp_file.name)
        tmp_file_path = tmp_file.name

    return FileResponse(
        path=tmp_file_path,
        media_type='application/pdf',
        filename="court_data.pdf",
        background=None
    )
