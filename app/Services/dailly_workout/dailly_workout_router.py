from fastapi import APIRouter,Depends
from app.Services.dailly_workout.dailly_workout import DailyWorkout
from app.Services.dailly_workout.daily_workout_schema import WorkoutSession

router = APIRouter()


@router.get("/daily_workout",response_model=WorkoutSession)
async def get_daily_workout(userId:str):
     try:
          return await DailyWorkout().get_response(userId)
     except Exception as e:
          return e