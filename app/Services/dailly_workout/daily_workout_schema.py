from pydantic import BaseModel, Field
from typing import List, Optional

class Exercise(BaseModel):
     id: str = Field(..., example="1,2,...")
     name: str = Field(..., example="Bench Press,Squat,Deadlift,Push-ups,Pull-ups,Other")
     sets: int = Field(..., ge=1)
     reps: int = Field(..., ge=1)
     weight_kg: float = Field(0.0, description="Weight used in kg for exercise")
     rest_time_sec: int = Field(45, description="Rest duration between sets")
     time_in_exercise: int = Field(..., ge=0)
     is_completed: bool = False

class WorkoutCategory(BaseModel):
     id: str = Field(..., example="1,2,...")
     category_name: str = Field(..., example="Upper Body,Lower Body,Full Body,Cardio,Flexibility,Other")
     exercises: List[Exercise]
     time_in_category: int = Field(..., ge=0)
     calories_burned_in_category: int = Field(..., ge=0)

class WorkoutSession(BaseModel):
     total_time_min: int = Field(..., ge=0)
     total_calories_burned: Optional[int] = 0
     title_of_workout: str = Field(..., example="Today's Workout Plan ,Today's session plan ,Today's workout session plan ...etc .")
     today_workout: List[WorkoutCategory]
     