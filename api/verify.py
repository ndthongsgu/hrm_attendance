from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.verify import verify_face
from schemas.verify_face import VerifyFaceResponse
import cv2
import numpy as np

router = APIRouter()

@router.post("/verify", response_model=VerifyFaceResponse)
async def verify_face_endpoint(employee_id: str = Form(...), file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    result = verify_face(image, employee_id)
    if result:
        return VerifyFaceResponse(status="success", employee_id=result, message="Face recognized")
    else:
        return VerifyFaceResponse(status="failed", message="Face not recognized")
