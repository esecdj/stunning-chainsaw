import os
from fastapi import FastAPI
from routers.auth_service import router as customer_auth_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
app = FastAPI()
origins = [
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "https://login.microsoftonline.com"  # React or frontend dev server
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # You can restrict to ["POST"] if needed
    allow_headers=["*"],
)
# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "your-very-secret-key"),  # Use a secure key here!
    same_site="lax",
    https_only=False  # Set to True in production
)
# Register Routers
app.include_router(customer_auth_router, prefix="", tags=["Customers"])

@app.get("/")
async def root():
    return {"message": "FastAPI MongoDB Scalable Project with Customers"}
