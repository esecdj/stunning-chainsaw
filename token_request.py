from pydantic import BaseModel


class TokenRequest(BaseModel):
    id_token: str
    access_token :str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"