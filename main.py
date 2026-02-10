from fastapi import FastAPI
from app.Services.food_scan.food_scan_router import router as food_scan_router
from app.Services.AI_coach.AI_coach_router import router as AI_coach_router
from app.Services.meal_generation.meal_generation_router import router as meal_generation_router
from app.Services.dailly_workout.dailly_workout_router import router as daily_workout_router
from app.Services.products.products_router import router as product_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
     title="Actyv AI",
     description="The fitness app developing is designed to offer a comprehensive fitness experience, combining personalized coaching with social interaction and a multi-vendor marketplace",
     version="1.0.0"
)
app.add_middleware(
     CORSMiddleware,
     allow_origins=["*"],
     allow_credentials=True,
     allow_methods=["*"],
     allow_headers=["*"],
)


app.include_router(food_scan_router,prefix="/v1",tags=["Food-scan"])
app.include_router(AI_coach_router,prefix="/v1",tags=["AI-coach"])
app.include_router(meal_generation_router,prefix="/v1",tags=["Meal-generation"])
app.include_router(daily_workout_router,prefix="/v1",tags=["Daily-workout"])
app.include_router(product_router,prefix="/v1",tags=["Product"])


if __name__ == "__main__":
     import uvicorn
     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)   