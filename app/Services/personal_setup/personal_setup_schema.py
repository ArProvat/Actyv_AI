from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class FitnessGoal(str, Enum):
     WEIGHT_LOSS = "WEIGHT_LOSS"
     MUSCLE_GAIN = "MUSCLE_GAIN"
     MAINTENANCE = "MAINTENANCE"
     ATHLETIC_PERFORMANCE = "ATHLETIC_PERFORMANCE"

class FitnessLevel(str, Enum):
     BEGINNER = "BEGINNER"
     INTERMEDIATE = "INTERMEDIATE"
     ADVANCED = "ADVANCED"

class BloodType(str, Enum):
     A_POSITIVE = "A_POSITIVE"
     A_NEGATIVE = "A_NEGATIVE"
     B_POSITIVE = "B_POSITIVE"
     B_NEGATIVE = "B_NEGATIVE"
     O_POSITIVE = "O_POSITIVE"
     O_NEGATIVE = "O_NEGATIVE"
     AB_POSITIVE = "AB_POSITIVE"
     AB_NEGATIVE = "AB_NEGATIVE"

class UserSetup(BaseModel):
     fitnessGoal: FitnessGoal
     fitnessLevel: FitnessLevel
     height: str = Field(..., example="5 feet 6 inch")
     weight: float = Field(..., example=69.25)
     age: int = Field(..., example=25)
     gender: str = Field(..., example="MALE")
     bloodType: Optional[BloodType] = None
     access_of_equipment: Optional[str] = Field(None, example="GYM")
     daysPerWeek: int = Field(..., ge=1, le=7)
     sessionLength: str = Field(..., example="20-30")
     injuries: Optional[str] = Field(None, example="Recently My Finger is broken")
     dietaryPreference: Optional[List[str]] = Field(None, example="VEGETARIAN")
     challenge: Optional[List[str]] = Field(None, example="VEGETARIAN")
     
     

     class Config:
          populate_by_name = True 
          json_schema_extra = {
               "example": {
                    "fitnessGoal": "WEIGHT_LOSS",
                    "fitnessLevel": "BEGINNER",
                    "height": "5 feet 6 inch",
                    "weight": 69.25,
                    "age": 25,
                    "gender": "MALE",
                    "bloodType": "A_POSITIVE",
                    "access_of_equipment": "GYM",
                    "daysPerWeek": 4,
                    "sessionLength": "20-30",
                    "injuries": "Recently My Finger is broken",
                    "dietaryPreference": ["VEGETARIAN"],
                    "challenge": ["VEGETARIAN",]
               }
          }



class StrategyRoadmap(BaseModel):
     daily_target_calories: dict = Field(
          ...,
          json_schema_extra={"example": {"value": 1850, "unit": "kcal/day", "display_text": "Daily Fuel Intake", "description": "Calculated for a steady 0.5kg/week weight loss."}}
     )
     macro_targets: list[dict] = Field(
          ...,
          json_schema_extra={"example": [{"name": "protein", "value": "138g", "description": "High protein to protect muscles."}]}
     )
     weekly_performance_goals: list[dict] = Field(
          ...,
          json_schema_extra={"example": [{"name": "exercise_burn", "value": 1200, "unit": "kcal/week"}]}
     )
     injury_protocol: dict = Field(
          ...,
          json_schema_extra={"example": {"status": "Active (Broken Finger)", "focus": "Hands-Free Hypertrophy"}}
     )
     active_challenges: list[dict] = Field(
          ...,
          json_schema_extra={"example": [{"title": "The 20-30 Sprint", "description": "Complete all 4 sessions.", "reward": "Consistency Badge"}]}
     )