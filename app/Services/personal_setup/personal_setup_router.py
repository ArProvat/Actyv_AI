
from fastapi import APIRouter, Depends, HTTPException
from app.Services.personal_setup.personal_setup import personalSetup
from app.Services.personal_setup.personal_setup_schema import UserSetup
from fastapi.encoders import jsonable_encoder

router = APIRouter()

personal_setup = personalSetup()

@router.post("/personal-setup/response/{user_id}")
async def get_response(user_id: str, personal_setup: UserSetup):
     return await personal_setup.get_response(user_id, personal_setup.dict())

@router.get("/personal-setup/{user_id}")
async def get_personal_setup(user_id: str,):
     result = await personal_setup.get_personal_setup(user_id)
     return jsonable_encoder(result)

@router.put("/personal-setup/{user_id}")
async def update_personal_setup(user_id: str, personal_setup: UserSetup):
     return await personal_setup.update_personal_setup(user_id, personal_setup.dict())
