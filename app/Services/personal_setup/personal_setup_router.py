
from fastapi import APIRouter, Depends, HTTPException
from app.Services.personal_setup.personal_setup import personalSetup
from app.Services.personal_setup.personal_setup_schema import UserSetup

router = APIRouter()

@router.post("/personal-setup/response/{userId}")
async def get_response(userId: str, personal_setup: UserSetup):
     return await personalSetup().get_response(userId, personal_setup.model_dump())

@router.get("/personal-setup/{userId}")
async def get_personal_setup(userId: str,):
     return await personalSetup().get_personal_setup(userId)

@router.put("/personal-setup/{userId}")
async def update_personal_setup(userId: str, personal_setup: UserSetup):
     return await personalSetup().update_personal_setup(userId, personal_setup.model_dump())

