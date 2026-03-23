import os
from core.settings import KNOWN_FACES_DIR
from typing import List, Tuple
from schemas.add_known_face import UploadedFileInfo

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}

def _is_valid_image(filename: str) -> bool:
    """Check if file has valid image extension"""
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS

def add_known_face(employee_id: str, files: List) -> Tuple[int, int, List[UploadedFileInfo]]:
    """
    Add multiple known face images for an employee
    Returns: (successful_count, failed_count, files_info_list)
    """
    # Create the employee folder if it doesn't exist
    employee_dir = os.path.join(KNOWN_FACES_DIR, employee_id)
    os.makedirs(employee_dir, exist_ok=True)

    files_info = []
    successful_count = 0
    failed_count = 0

    # Process each file
    for file in files:
        try:
            # Validate file extension
            if not _is_valid_image(file.filename):
                files_info.append(UploadedFileInfo(
                    filename=file.filename,
                    status="failed",
                    message="Invalid file type. Only image files are allowed (jpg, jpeg, png, gif, bmp)"
                ))
                failed_count += 1
                continue

            # Check if file is not empty
            if file.size == 0:
                files_info.append(UploadedFileInfo(
                    filename=file.filename,
                    status="failed",
                    message="File is empty"
                ))
                failed_count += 1
                continue

            # Save the file
            file_path = os.path.join(employee_dir, file.filename)
            with open(file_path, "wb") as buffer:
                content = file.file.read()
                buffer.write(content)
            
            files_info.append(UploadedFileInfo(
                filename=file.filename,
                status="success",
                message=f"Image saved successfully"
            ))
            successful_count += 1

        except Exception as e:
            files_info.append(UploadedFileInfo(
                filename=file.filename,
                status="failed",
                message=f"Error saving file: {str(e)}"
            ))
            failed_count += 1

    return successful_count, failed_count, files_info
