from pydantic import BaseModel, EmailStr

class RequestResetPasswordRequestDTO(BaseModel):
    email: EmailStr

class RequestResetPasswordResponseDTO(BaseModel):
    message: str

