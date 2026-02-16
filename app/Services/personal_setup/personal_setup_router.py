

from fastapi import APIRouter, Depends, HTTPException
from app.Services.personal_setup.personal_setup import personalSetup
from app.Services.personal_setup.personal_setup_schema import UserSetup
from app.utils.auth.auth import get_current_user

router = APIRouter()

personal_setup = personalSetup()

@router.post("/personal-setup/response/{user_id}")
async def get_response(user_id: str, personal_setup: UserSetup):
     return await personal_setup.get_response(user_id, personal_setup.dict())

@router.get("/personal-setup/{user_id}")
async def get_personal_setup(user_id: str,):
     return await personal_setup.get_personal_setup(user_id)

@router.put("/personal-setup/{user_id}")
async def update_personal_setup(user_id: str, personal_setup: UserSetup):
     return await personal_setup.update_personal_setup(user_id, personal_setup.dict())
