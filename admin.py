from typing import List, Literal, Optional
from pydantic import BaseModel, BeforeValidator, Field
from typing import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class AdminModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    emails : Optional[List[str]] = Field(default_factory=list)
