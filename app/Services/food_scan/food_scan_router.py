from fastapi import APIRouter, File, UploadFile, Depends
from app.Services.food_scan.food_scan import food_scan_service
from app.modules.auth.auth import verify_token
from fastapi import HTTPException

router = APIRouter()
food_scan_instance =food_scan_service()

@router.post("/food-scan")
async def food_scan(file: UploadFile = File(...),user: dict = Depends(verify_token)):
     try:
          if not user:
               raise HTTPException(status_code=401, detail="Unauthorized")
          if not file:
               raise HTTPException(status_code=400, detail="No file provided")
          if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
               raise HTTPException(status_code=400, detail="Invalid file type")
          return await food_scan_instance.generate_response(await file.read())
     except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))