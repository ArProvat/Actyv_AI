
from fastapi import APIRouter,HTTPException
from app.DB.mongodb.mongodb import MongoDB
from app.DB.vectorDB.vectordb import VectorDB


router = APIRouter()
vector_db = VectorDB()
mongodb = MongoDB()


@router.post("/add_product")
async def add_product(id:str):
     try:
          product = await mongodb.get_product(id)
          description = product.get("description")

          await vector_db.add_product(description,id)
          return {"message":"Product added successfully"}
     except Exception as e:
          raise HTTPException(status_code=500,detail=str(e))

@router.get("/search_product")
async def search_product(query:str,limit:int=10):
     try:
          results = await vector_db.search_product(query,limit)
          if not results:
               raise HTTPException(status_code=404,detail="No results found")
          product = await mongodb.get_multiple_products(results)
          return {"results":product}
     except Exception as e:
          raise HTTPException(status_code=500,detail=str(e))

@router.delete("/delete_product")
async def delete_product(product_id:str):
     try:
          await vector_db.delete_product(product_id)
          return {"message":"Product deleted successfully"}
     except Exception as e:
          raise HTTPException(status_code=500,detail=str(e))

          
     
