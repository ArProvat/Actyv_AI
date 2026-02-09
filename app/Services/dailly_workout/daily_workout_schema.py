from pydantic import BaseModel, Field
from typing import List, Optional

class Exercise(BaseModel):
     name: str = Field(..., example="Bench Press")
     sets: int = Field(..., ge=1)
     reps: int = Field(..., ge=1)
     weight_kg: float = Field(0.0, description="Weight used in kg for exercise")
     rest_time_sec: int = Field(45, description="Rest duration between sets")
     is_completed: bool = False

class WorkoutCategory(BaseModel):
     category_name: str = Field(..., example="Upper Body")
     exercises: List[Exercise]
     time_in_category: int = Field(..., ge=0)

class WorkoutSession(BaseModel):
     total_time_min: int = Field(..., ge=0)
     total_calories_burned: Optional[int] = 0
     today_workout: List[WorkoutCategory]
     