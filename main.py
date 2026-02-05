from fastapi import FastAPI
from app.Services.food_scan.food_scan_router import router as food_scan_router

app = FastAPI(
     title="Actyv AI",
     description="he fitness app developing is designed to offer a comprehensive fitness experience, combining personalized coaching with social interaction and a multi-vendor marketplace,
     version="1.0.0"
)

app.include_router(food_scan_router,prefix="/api/v1",tags=["food-scan"])

if __name__ == "__main__":
     import uvicorn
     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)   