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
               }
          }



class StrategyRoadmap(BaseModel):
     daily_target_calories: List[dict] = Field(..., example=[
          "value",
          "unit",
          "display_text",
          "description"]),
     macro_targets:List[dict] = Field(..., example=[
          "name",
          "value",
          "description"]),
     weekly_performance_goals:List[dict] = Field(..., example=[
          "exercise_burn",
          "sleep_target"]),
     injury_protocol: dict = Field(..., example=[
          "status",
          "focus",
          "description"]),
     active_challenges: List[dict] = Field(..., example=[
          "title",
          "description",
          "reward"])
     
class StrategyRoadmap(BaseModel):
     daily_target_calories: dict = Field(..., example={"value": 1850, "unit": "kcal/day", "display_text": "Daily Fuel Intake", "description": "Calculated for a steady 0.5kg/week weight loss while maintaining energy for workouts."})
     macro_targets: list[dict] = Field(..., example=[{"name":"protein",  "value": "138g", "description": "High protein to protect your muscles during weight loss."  },{"name":"carbs", "value": "185g", "description": "Complex carbs to fuel your 20-30 minute gym sessions." } ,{"name":"fats", "value": "51g", "description": "Healthy fats for hormonal balance and finger bone recovery." } ])
     weekly_performance_goals: list[dict] = Field(..., example=[{"name":"exercise_burn", "value": 1200, "unit": "kcal/week", "display_text": "Weekly Activity Burn", "description": "Total calories to burn across your 4 gym sessions."},{"name":"sleep_target", "value": 8, "unit": "hours/night", "display_text": "Recovery Sleep", "description": "Critical for tissue repair (finger) and metabolic health."}])
     injury_protocol: dict = Field(..., example={"status": "Active (Broken Finger)", "focus": "Hands-Free Hypertrophy", "description": "Your plan will exclude 'Grip' exercises. We will use Smith machines, leg presses, and seated core work to keep you safe."})
     active_challenges: list[dict] = Field(..., example=[{"title": "The 20-30 Sprint", "description": "Complete all 4 sessions this week within your 30-minute window.", "reward": "Consistency Badge"},{"title": "Hydration Station", "description": "Drink 3 liters of water daily to support bone healing and digestion.", "reward": "100 XP"}])
