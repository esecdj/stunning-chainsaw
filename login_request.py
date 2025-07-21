from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class EmailRequest(BaseModel):
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class TOTPVerifyRequest(BaseModel):
    email: EmailStr
    totp: str

class MFACombinedLoginRequest(BaseModel):
    email: EmailStr
    otp: str
    totp: str