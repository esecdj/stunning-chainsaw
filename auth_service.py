import base64
import os
import time
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, update
from auth import mfa, otp
from database import get_db
from models.consultant import Consultant
from models.customer import Customer
from schemas.consultant import ConsultantSchema
from schemas.customer import CustomerSchema
from utils.email_utils import generate_verification_token, send_otp_verification_email, send_welcome_email
from utils.saml import get_saml_settings, init_saml_auth
router = APIRouter()
import jwt
from datetime import datetime, timedelta, timezone
from schemas.requests.login_request import EmailRequest, MFACombinedLoginRequest, OTPVerifyRequest, TOTPVerifyRequest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse
SECRET_KEY = os.getenv("SECRET_KEY", "SECRET_KEY")
AES_SECRET_KEY = os.getenv("AES_SECRET_KEY", "AES_SECRET_KEY").encode()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Function to create JWT Token
def create_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + expires_delta  # Fixed deprecated utcnow()
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def is_consultant_email(email: str) -> bool:
    return email.endswith("@esecforte.com")


@router.post("/sso/acs/", response_model=ConsultantSchema)
async def saml_acs(request: Request, db: AsyncSession = Depends(get_db)):
    # Step 1: Process SAML response
    saml_auth = await init_saml_auth(request)
    saml_auth.process_response()
    errors = saml_auth.get_errors()

    if errors:
        raise HTTPException(status_code=400, detail={"error": "SAML Error", "details": errors})

    if not saml_auth.is_authenticated():
        raise HTTPException(status_code=401, detail="Authentication failed")

    # Step 2: Extract attributes
    attributes = saml_auth.get_attributes()
    print("[SAML Attributes]", attributes)

    email = attributes.get("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress", [None])[0]
    name = attributes.get("http://schemas.microsoft.com/identity/claims/displayname", [None])[0]
    phone = attributes.get("Telephone", [None])[0]
    azure_id = attributes.get("http://schemas.microsoft.com/identity/claims/objectidentifier", [None])[0]

    if not email:
        raise HTTPException(status_code=400, detail="Email not found in SAML attributes")

    # Step 3: Check if consultant already exists
    result = await db.execute(select(Consultant).where(Consultant.mail == email))
    existing_consultant = result.scalar_one_or_none()

    if existing_consultant:
        raise HTTPException(status_code=400, detail="Consultant email already exists!")

    consultant = ConsultantSchema(
        azure_id=azure_id,
        display_name=name,
        mail=email,
        mobile_phone=phone or "",
        role="CONSULTANT"
    )
    new_consultant = Consultant(**consultant.model_dump(exclude_unset=True))

    db.add(new_consultant)
    await db.commit()
    await db.refresh(new_consultant)
    return new_consultant

@router.get("/metadata/")
async def metadata():
    from onelogin.saml2.metadata import OneLogin_Saml2_Metadata
    settings = get_saml_settings()
    metadata, errors = OneLogin_Saml2_Metadata.builder(settings._sp, settings._security)

    if errors:
        raise HTTPException(status_code=500, detail=f"Metadata error: {errors}")
    return HTMLResponse(content=metadata, media_type="application/xml")

@router.post("/signup/", response_model=CustomerSchema)
async def signup(customer: CustomerSchema, db: AsyncSession = Depends(get_db)):
    # 1. Check if customer already exists
    
    result = await db.execute(select(Customer).where(Customer.customer_email == customer.customer_email))
    existing_customer = result.scalar_one_or_none()
    
    if existing_customer:
        raise HTTPException(status_code=400, detail="Customer email already exists!")

    # 2. Create verification token
    token = await generate_verification_token(customer.customer_email)
    expiry_timestamp = int(time.time()) + 86400  # 1 day validity

    # 3. Prepare customer data
    customer_dict = customer.model_dump(exclude_unset=True)
    customer_dict.update({
        "customer_verification_token": token,
        "customer_verification_token_expiry": expiry_timestamp,
        "customer_status": "UNVERIFIED",
        "customer_email_verified": False
    })

    new_customer = Customer(**customer_dict)
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)

    # 4. Send email
    await send_welcome_email(customer.customer_email, token, db)

    return new_customer

user_sessions = {}

@router.post("/request-otp")
async def request_otp(request: Request, data: EmailRequest, db: AsyncSession = Depends(get_db)):
    email = data.email
    if is_consultant_email(email):
        # Consultant → return SSO URL
        request_id = uuid.uuid4().hex
        user_sessions[request_id] = {"email": email}
        
        saml_auth = await init_saml_auth(request, request_id)
        sso_url = saml_auth.login()
        return JSONResponse({
            "type": "consultant",
            "sso_redirect_url": sso_url
        })
    
    result = await db.execute(select(Customer).where(Customer.customer_email == email))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if customer.customer_status != "APPROVED":
        raise HTTPException(status_code=403, detail="Customer not approved")

    code = otp.generate_otp()
    await otp.store_otp(email, code, db)
    print(f"[DEBUG] OTP for {email}: {code}")
    await send_otp_verification_email(email, code, db)
    
    mfa_enabled = customer.is_mfa_enabled

    return {
        "message": "OTP sent to email (check console)",
        "email": email,
        "mfa_setup": mfa_enabled
    }

@router.post("/mfa-login")
async def mfa_login(data: MFACombinedLoginRequest, db: AsyncSession = Depends(get_db)):
    if not await otp.validate_otp(data.email, data.otp, db):
        raise HTTPException(status_code=401, detail="Invalid OTP")
    if not await mfa.verify_totp(data.email, data.totp, db):
        raise HTTPException(status_code=401, detail="Invalid Authenticator Code")
    result = await db.execute(select(Customer).where(Customer.customer_email == data.email))
    existing_customer = result.scalar_one_or_none()
    if not existing_customer:
        raise HTTPException(status_code=404, detail="CustomerResponseModel not found")
    token = create_token({"sub": data.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/verify-otp")
async def verify_otp(data: OTPVerifyRequest, db: AsyncSession = Depends(get_db)):
    if not await otp.validate_otp(data.email, data.otp, db):
        raise HTTPException(status_code=401, detail="Invalid OTP")

    result = await db.execute(select(Customer).where(Customer.customer_email == data.email))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="CustomerResponseModel not found")

    mfa_enabled = customer.is_mfa_enabled
    if mfa_enabled:
        return {"message": "MFA already setup", "mfa_setup": True}

    secret = await mfa.generate_totp_secret(data.email)
    qr = await mfa.generate_qr_code(data.email, secret)

    await db.execute(update(Customer).where(Customer.customer_email == data.email).values(mfa_secret=secret))
    await db.commit()
    with open("mfa_qr.png", "wb") as f:
        f.write(base64.b64decode(qr))
    return {"qr_code_base64": qr, "email": data.email, "mfa_setup": False}

@router.post("/verify-totp")
async def verify_totp(data: TOTPVerifyRequest, db: AsyncSession = Depends(get_db)):
    if not await mfa.verify_totp(data.email, data.totp, db):
        raise HTTPException(status_code=401, detail="Invalid Authenticator Code")

    await db.execute(update(Customer).where(Customer.customer_email == data.email).values(is_mfa_enabled=True))
    await db.commit()

    return {"message": "Authentication successful!"}
