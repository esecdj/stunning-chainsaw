from pydantic import BaseModel, EmailStr


class CustomerLogin(BaseModel):
    customer_email: EmailStr
    customer_password: str