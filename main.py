from fastapi import FastAPI
from app.Services.food_scan.food_scan_router import router as food_scan_router
from app.Services.AI_coach.AI_coach_router import router as AI_coach_router
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


app.include_router(food_scan_router,prefix="/api/v1",tags=["Food-scan"])
app.include_router(AI_coach_router,prefix="/api/v1",tags=["AI-coach"])

if __name__ == "__main__":
     import uvicorn
     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)   