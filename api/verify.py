from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.verify import verify_face
from schemas.verify_face import VerifyFaceResponse
import cv2
import numpy as np
import logging
from deepface import DeepFace
import tempfile
import os

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/verify", response_model=VerifyFaceResponse)
async def verify_face_endpoint(employee_id: str = Form(...), file: UploadFile = File(...)):
    """
    Verify employee face against their known faces
    
    Args:
        employee_id: The employee ID to verify against
        file: Image file containing the face to verify
    
    Returns:
        VerifyFaceResponse with:
        - status: "success" if face matches, "failed" otherwise
        - employee_id: The verified employee ID if successful
        - message: Human-readable message
    """
    temp_path = None
    try:
        # Validate input
        if not file.content_type.startswith("image/"):
            logger.warning(f"Invalid file type for employee {employee_id}: {file.content_type}")
            raise HTTPException(
                status_code=400, 
                detail="File must be an image"
            )
        
        if not employee_id or not employee_id.strip():
            logger.warning("Employee ID is empty")
            raise HTTPException(
                status_code=400, 
                detail="Employee ID is required"
            )

        # Read and decode image
        contents = await file.read()
        
        if len(contents) == 0:
            logger.warning(f"Empty file received for employee {employee_id}")
            raise HTTPException(
                status_code=400, 
                detail="Image file is empty"
            )
        
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            logger.warning(f"Failed to decode image for employee {employee_id}")
            raise HTTPException(
                status_code=400, 
                detail="Invalid or corrupted image file"
            )

        # Save to temp file for proper face detection
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            temp_path = tmp_file.name
            cv2.imwrite(temp_path, image)

        # Check if face exists in image with enforce_detection=False (more lenient)
        try:
            logger.info(f"Checking for face in image for employee {employee_id}")
            # Use enforce_detection=False to avoid strict face detection failures
            # We'll validate face quality separately if needed
            face_objs = DeepFace.extract_faces(img_path=temp_path, enforce_detection=False)
            
            logger.info(f"Face detection result: {len(face_objs) if face_objs else 0} faces found")
            
            if not face_objs or len(face_objs) == 0:
                logger.warning(f"No face detected in image for employee {employee_id}")
                return VerifyFaceResponse(
                    status="failed", 
                    employee_id=None,
                    message="Không phát hiện khuôn mặt trong ảnh. Vui lòng chụp lại với khuôn mặt rõ ràng."
                )
        except Exception as e:
            logger.error(f"Face detection error for employee {employee_id}: {str(e)}", exc_info=True)
            return VerifyFaceResponse(
                status="failed", 
                employee_id=None,
                message=f"Lỗi xác minh khuôn mặt: {str(e)}"
            )

        # Verify face against known faces
        logger.info(f"Starting face verification for employee {employee_id}")
        result = verify_face(image, employee_id)
        
        if result:
            logger.info(f"Face verification successful for employee {employee_id}")
            return VerifyFaceResponse(
                status="success", 
                employee_id=result, 
                message="Xác minh khuôn mặt thành công"
            )
        else:
            logger.info(f"Face verification failed for employee {employee_id}")
            return VerifyFaceResponse(
                status="failed", 
                employee_id=None,
                message="Khuôn mặt không khớp với dữ liệu đã lưu. Vui lòng thử lại hoặc liên hệ quản trị viên."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during face verification for employee {employee_id}: {str(e)}", exc_info=True)
        return VerifyFaceResponse(
            status="failed",
            employee_id=None,
            message=f"Lỗi xác minh khuôn mặt: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the face verification service
    """
    return {"status": "ok", "service": "face-verification"}

