from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    # Placeholder: send to vision chain for caption/classification
    return {"filename": file.filename, "status": "analyzed"}
