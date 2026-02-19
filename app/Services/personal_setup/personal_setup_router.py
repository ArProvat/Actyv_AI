
from app.modules.auth.auth import verify_token
from fastapi import APIRouter, Depends, HTTPException
from app.Services.personal_setup.personal_setup import personalSetup
from app.Services.personal_setup.personal_setup_schema import UserSetup

router = APIRouter()

@router.post("/personal-setup/response")
async def get_response(personal_setup: UserSetup, user: dict = Depends(verify_token)):
     userId = user["id"]
     return await personalSetup().get_response(userId, personal_setup.model_dump())

@router.get("/personal-setup")
async def get_personal_setup(user: dict = Depends(verify_token)):
     userId = user["id"]
     return await personalSetup().get_personal_setup(userId)

@router.put("/personal-setup")
async def update_personal_setup( personal_setup: UserSetup, user: dict = Depends(verify_token)):
     userId = user["id"]
     return await personalSetup().update_personal_setup(userId, personal_setup.model_dump())

