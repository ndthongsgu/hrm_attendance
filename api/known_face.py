from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.known_face import add_known_face
from schemas.add_known_face import AddKnownFaceResponse

router = APIRouter()

@router.post("/add_known_face", response_model=AddKnownFaceResponse)
async def add_known_face_endpoint(employee_id: str = Form(...), file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    message = add_known_face(employee_id, file)
    return AddKnownFaceResponse(status="success", message=message)
