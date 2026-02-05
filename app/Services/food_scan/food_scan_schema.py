from pydantic import BaseModel, Field

class FoodScanResponse(BaseModel):
     food_name: str = Field(..., description="Name of the food")
     ingredients: list[str] = Field(..., description="List of ingredients")
     calories: int = Field(..., description="Calories in the food")
     protein: int = Field(..., description="Protein in the food")
     fat: int = Field(..., description="Fat in the food")
     carbs: int = Field(..., description="Carbs in the food")
     fiber: int = Field(..., description="Fiber in the food")
     total_mass: int = Field(..., description="Total mass of the food")
     health_score: int = Field(..., description="Health score of the food")
     confidence: float = Field(..., description="Confidence score of the food")








