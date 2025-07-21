
from pydantic import BaseModel


class PasswordRequestModel(BaseModel):
    password: str