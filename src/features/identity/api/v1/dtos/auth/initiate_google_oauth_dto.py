from pydantic import BaseModel

class InitiateGoogleOauthResponseDTO(BaseModel):
    url: str