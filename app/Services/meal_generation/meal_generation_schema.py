from pydantic import BaseModel, Field
from typing import List, Optional

class FoodItem(BaseModel):
     id:int = Field(..., example="1,2,...")
     name: str = Field(..., example="Avocado Toast")
     ingredients: List[str] = Field(default_factory=list, example=["Whole grain bread", "Avocado", "Chili flakes"])
     quantity: Optional[int] = Field(..., example="2 ")
     unit: Optional[str] = Field(..., example="slice,gram,kg,piece")
     total_calories: float = Field(..., ge=0, description="Total calories in the food item")
     fat_g: float = Field(..., ge=0, description="Fat in grams")
     carbs_g: float = Field(..., ge=0, description="Carbohydrates in grams")
     protein_g: float = Field(..., ge=0, description="Protein in grams")
     is_completed: bool = Field(..., example="Only False")

class MealCategory(BaseModel):
     # e.g., "Morning", "Lunch", "Evening Snack", "Dinner"
     id:int = Field(..., example="1,2,...")
     category_name: str = Field(..., example="Breakfast,Lunch,Post_Workout,Pre_Workout,Dinner")
     list_of_food: List[FoodItem] = Field(default_factory=list, example=[{"id": "1,2,... ","name": "Avocado Toast", "ingredients": ["Whole grain bread", "Avocado", "Chili flakes"], "quantity": 2, "unit": "slice", "total_calories": 300, "fat_g": 10, "carbs_g": 20, "protein_g": 5,"is_completed": "Only False"}])

class DailyMealLog(BaseModel):
     meals: List[MealCategory]
