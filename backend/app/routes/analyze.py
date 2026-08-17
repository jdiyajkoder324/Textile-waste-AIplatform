from fastapi import APIRouter
from pydantic import BaseModel
from app.services.analyzer import AnalyzerService

router = APIRouter()
service = AnalyzerService()

class InputText(BaseModel):
    text: str


@router.post("/analyze")
def analyze(data: InputText):

    result = service.analyze_sentiment(data.text)

    return {
        "input": data.text,
        "analysis": result
    }