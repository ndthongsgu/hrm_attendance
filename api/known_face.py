from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from services.known_face import add_known_face
from schemas.add_known_face import AddKnownFaceResponse

router = APIRouter()

@router.post("/add_known_face", response_model=AddKnownFaceResponse)
async def add_known_face_endpoint(employee_id: str = Form(...), files: List[UploadFile] = File(...)):
    """
    Upload multiple images for known face recognition
    
    Parameters:
    - employee_id: The ID of the employee
    - files: Multiple image files (jpg, jpeg, png, gif, bmp)
    
    Returns:
    - status: 'success' if at least one file uploaded, 'partial' if some failed, 'failed' if all failed
    - message: Summary message
    - employee_id: The employee ID
    - total_files: Total number of files submitted
    - successful_uploads: Number of successfully uploaded files
    - failed_uploads: Number of failed uploads
    - files_info: Detailed info for each file
    """
    if not employee_id or not employee_id.strip():
        raise HTTPException(status_code=400, detail="employee_id is required")
    
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="At least one file is required")
    
    # Validate file count
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Cannot upload more than 50 files at once")

    # Process all files
    successful_count, failed_count, files_info = add_known_face(employee_id, files)
    
    # Determine overall status
    if successful_count == 0:
        overall_status = "failed"
        status_message = f"Failed to upload all {len(files)} files"
    elif failed_count == 0:
        overall_status = "success"
        status_message = f"Successfully uploaded {successful_count} image(s) for employee {employee_id}"
    else:
        overall_status = "partial"
        status_message = f"Uploaded {successful_count}/{len(files)} images. {failed_count} file(s) failed"
    
    if successful_count == 0:
        raise HTTPException(
            status_code=400, 
            detail=status_message
        )
    
    return AddKnownFaceResponse(
        status=overall_status,
        message=status_message,
        employee_id=employee_id,
        total_files=len(files),
        successful_uploads=successful_count,
        failed_uploads=failed_count,
        files_info=files_info
    )
