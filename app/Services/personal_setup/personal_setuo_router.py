

from fastapi import APIRouter, Depends, HTTPException
from app.Services.personal_setup.personal_setup import personalSetup
from app.Services.personal_setup.personal_setup_schema import UserSetup
from app.Services.auth.auth_router import get_current_user

router = APIRouter()

personal_setup = personalSetup()

@router.post("/personal_setup")
async def create_personal_setup(user_id: str, personal_setup: UserSetup):
    try:
        return await personal_setup.get_response(user_id, personal_setup)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/personal_setup/{user_id}")
async def get_personal_setup(user_id: str):
    try:
        return await personal_setup.get_personal_setup(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

