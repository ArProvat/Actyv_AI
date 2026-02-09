

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

class Exercise(BaseModel):
     name: str = Field(..., example="Bench Press")
     sets: int = Field(..., ge=1)
     reps: int = Field(..., ge=1)
     weight_kg: float = Field(0.0, description="Weight used in kilograms")
     rest_time_sec: int = Field(45, description="Rest duration between sets")
     is_completed: bool = False

class WorkoutCategory(BaseModel):
     category_name: str = Field(..., example="Upper Body")
     category_exercises: List[Exercise]
     time_in_category: int = Field(..., ge=0)

class WorkoutSession(BaseModel):
     workout_id: UUID = Field(default_factory=uuid4)
     user_id: UUID
     date: datetime = Field(default_factory=datetime.now)
     total_time_min: int = Field(..., ge=0)
     total_calories_burned: Optional[int] = 0
     today_workout: List[WorkoutCategory]
     
     class Config:
          schema_extra = {
               "example": {
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "total_time_min": 45,
                    "total_calories_burned": 320,
                    "today_workout": [
                         {
                         "category_name": "Upper Body",
                         "time_in_category": 20,
                         "category_exercises": [
                              {"name": "Bench Press", "sets": 3, "reps": 12, "weight_kg": 70, "rest_time_sec": 45, "is_completed": False}
                         ]
                         },
                         {
                         "category_name": "Abs",
                         "time_in_category": 10,
                         "category_exercises": [
                              {"name": "Plank", "sets": 3, "reps": 1, "weight_kg": 0, "rest_time_sec": 45, "is_completed": False}
                         ]
                         }
                    ]
               }
          }