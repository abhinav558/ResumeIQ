from fastapi import APIRouter, UploadFile, File
from app.services.parser import extract_text
from app.services.analyzer import analyze_resume


router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)


@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    content = await file.read()

    text = extract_text(
        content,
        file.filename
    )

    result = analyze_resume(text)

    return result