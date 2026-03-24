from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import List
import os
from services.known_face import add_known_face, get_known_faces
from schemas.add_known_face import AddKnownFaceResponse, GetKnownFacesResponse
from core.settings import KNOWN_FACES_DIR

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

@router.get("/list/{employee_id}", response_model=GetKnownFacesResponse)
async def get_known_faces_endpoint(employee_id: str):
    """
    Get list of known face images for an employee
    
    Parameters:
    - employee_id: The ID of the employee
    
    Returns:
    - status: 'success' if operation successful
    - employee_id: The employee ID
    - total_images: Total number of known face images
    - images: List of image info with filename and URL
    """
    if not employee_id or not employee_id.strip():
        raise HTTPException(status_code=400, detail="employee_id is required")
    
    # Get the list of known faces
    images = get_known_faces(employee_id)
    
    return GetKnownFacesResponse(
        status="success",
        employee_id=employee_id,
        total_images=len(images),
        images=images
    )

@router.delete("/{employee_id}/{filename}")
async def delete_known_face_image(employee_id: str, filename: str):
    """
    Delete a specific known face image for an employee
    
    Parameters:
    - employee_id: The ID of the employee
    - filename: The filename of the image to delete
    
    Returns:
    - Success message
    """
    if not employee_id or not employee_id.strip():
        raise HTTPException(status_code=400, detail="employee_id is required")
    
    if not filename or not filename.strip():
        raise HTTPException(status_code=400, detail="filename is required")
    
    # Build file path
    file_path = os.path.join(KNOWN_FACES_DIR, employee_id, filename)
    
    # Security check - ensure path doesn't escape known_faces directory
    if not os.path.abspath(file_path).startswith(os.path.abspath(KNOWN_FACES_DIR)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if file exists
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        # Delete the file
        os.remove(file_path)
        return {"status": "success", "message": f"Image {filename} deleted successfully", "employee_id": employee_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@router.get("/{employee_id}/{filename}")
async def get_known_face_image(employee_id: str, filename: str):
    """
    Get a specific known face image for an employee
    
    Parameters:
    - employee_id: The ID of the employee
    - filename: The filename of the image
    
    Returns:
    - Image file
    """
    if not employee_id or not employee_id.strip():
        raise HTTPException(status_code=400, detail="employee_id is required")
    
    if not filename or not filename.strip():
        raise HTTPException(status_code=400, detail="filename is required")
    
    # Build file path
    file_path = os.path.join(KNOWN_FACES_DIR, employee_id, filename)
    
    # Security check - ensure path doesn't escape known_faces directory
    if not os.path.abspath(file_path).startswith(os.path.abspath(KNOWN_FACES_DIR)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if file exists
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Return the file
    return FileResponse(file_path, media_type="image/jpeg")
