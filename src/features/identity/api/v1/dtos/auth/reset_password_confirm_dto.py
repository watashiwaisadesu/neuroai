from pydantic import BaseModel, EmailStr

class VerifyResetPasswordRequestDTO(BaseModel):
    new_password: str
    confirm_new_password: str

class ResetPasswordConfirmResponseDTO(BaseModel):
    message: str = "Password has been reset successfully."
