from pydantic import BaseModel
from typing import List, Optional

class AddKnownFaceRequest(BaseModel):
    employee_id: str

class UploadedFileInfo(BaseModel):
    filename: str
    status: str
    message: Optional[str] = None

class AddKnownFaceResponse(BaseModel):
    status: str
    message: str
    employee_id: str
    total_files: int
    successful_uploads: int
    failed_uploads: int
    files_info: List[UploadedFileInfo]

class KnownFaceInfo(BaseModel):
    filename: str
    url: str

class GetKnownFacesResponse(BaseModel):
    status: str
    employee_id: str
    total_images: int
    images: List[KnownFaceInfo]
