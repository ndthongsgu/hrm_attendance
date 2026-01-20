from pydantic import BaseModel

class AddKnownFaceRequest(BaseModel):
    employee_id: str

class AddKnownFaceResponse(BaseModel):
    status: str
    message: str
