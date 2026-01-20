from pydantic import BaseModel

class VerifyRequest(BaseModel):
    employee_id: str
    image: bytes  # or something, but since it's file, perhaps not needed
