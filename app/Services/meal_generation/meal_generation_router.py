from fastapi import APIRouter,Depends,HTTPException
from app.Services.meal_generation.meal_generation import MealGeneration
from app.Services.meal_generation.meal_generation_schema import DailyMealLog
from app.DB.mongodb.mongodb import MongoDB

router = APIRouter()

meal_generation = MealGeneration()

@router.post("/meal_generation")
async def meal_generation_router(userId:str):
     try:
          return await meal_generation.get_response(userId)
     except Exception as e:
          return HTTPException(status_code=500,detail=str(e))