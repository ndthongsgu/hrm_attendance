from pydantic import BaseModel
from typing import Optional

class VerifyFaceRequest(BaseModel):
    employee_id: str

class VerifyFaceResponse(BaseModel):
    status: str
    employee_id: Optional[str] = None
    message: Optional[str] = None
