from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.config.settings import settings
from app.utils.embedding.embedding import EmbeddingService
from app.Services.products.products_schema import Product


class ProductService:
     def __init__(self ):
          self.client = AsyncIOMotorClient(settings.DATABASE_URL)
          self.db = self.client[settings.DATABASE_NAME]
          self.product_collection = self.db["products"]
          self.embedding_service = EmbeddingService()

     async def create_product_with_embedding(self, product_data: dict) -> Product:
          """Create a product and generate its embedding"""
          product = Product(**product_data)
          
          product_text = self.embedding_service.create_product_text(product)
          embedding = self.embedding_service.generate_embedding(product_text)
          product.embedding = embedding
          
          result = self.products_collection.insert_one(
               product.model_dump(by_alias=True, exclude={"id"})
          )
          product.id = result.inserted_id
          
          return product
     
     async def update_product_with_embedding(self, product_id: str , product_data: dict) -> bool:
          """Update embedding for an existing product"""
          product_exists = await self.products_collection.find_one({"_id": ObjectId(product_id)})
          if not product_exists:
               return False
          
          product = Product(**product_data)
          product_text = self.embedding_service.create_product_text(product)
          embedding = self.embedding_service.generate_embedding(product_text)
          
          await self.products_collection.update_one(
               {"_id": ObjectId(product_id)},
               {"$set": {"embedding": embedding}}
          )
          return True

     async def get_product_by_id(self, product_id: str) -> Optional[Product]:
          """Get a product by its ID"""
          product_data = await self.products_collection.find_one({"_id": ObjectId(product_id)})
          if not product_data:
               return None
          return Product(**product_data)


     async def vector_search_products(
          self,
          query_embedding: List[float],
          limit: int = 10,
          filters: Optional[Dict[str, Any]] = None,
          min_score: float = 0.5
     ) -> List[Dict]:
          """
          Perform vector search on products
          
          Args:
               query_embedding: The embedding vector to search with
               limit: Number of results to return
               filters: Additional filters (category, price range, etc.)
               min_score: Minimum similarity score (0-1)
          """
          
          pipeline = [
               {
                    "$vectorSearch": {
                         "index": "product_vector_index",
                         "path": "embedding",
                         "queryVector": query_embedding,
                         "numCandidates": limit * 10,  # Over-fetch for better results
                         "limit": limit
                    }
               },
               {
                    "$addFields": {
                         "score": {"$meta": "vectorSearchScore"}
                    }
               }
          ]
          
          if filters:
               match_conditions = {}
               
               if "category" in filters:
                    match_conditions["category"] = filters["category"]
               
               if "status" in filters:
                    match_conditions["status"] = filters["status"]
               else:
                    match_conditions["status"] = "ACTIVE"  
               
               if "price_range" in filters:
                    match_conditions["price"] = {
                         "$gte": filters["price_range"].get("min", 0),
                         "$lte": filters["price_range"].get("max", float('inf'))
                    }
               
               if "min_rating" in filters:
                    match_conditions["averageRating"] = {"$gte": filters["min_rating"]}
               
               if match_conditions:
                    pipeline.append({"$match": match_conditions})
          
          pipeline.append({
               "$match": {
                    "score": {"$gte": min_score}
               }
          })
          
          pipeline.append({
               "$project": {
                    "_id": 1,
                    "name": 1,
                    "category": 1,
                    "description": 1,
                    "price": 1,
                    "discount": 1,
                    "averageRating": 1,
                    "totalReview": 1,
                    "features": 1,
                    "score": 1
               }
          })
          
          results = list(self.products_collection.aggregate(pipeline))
          return results
     
     async def search_by_text_query(
          self,
          query: str,
          limit: int = 10,
          filters: Optional[Dict[str, Any]] = None
     ) -> List[Dict]:
          """Search products using natural language query"""
          
          query_embedding = self.embedding_service.generate_embedding(query)
          
          return await self.vector_search_products(
               query_embedding=query_embedding,
               limit=limit,
               filters=filters
          )

     async def get_similar_products(
          self,
          product_id: str,
          limit: int = 5
     ) -> List[Dict]:
          """Find similar products based on a given product"""
          
          product_data = await self.products_collection.find_one({"_id": ObjectId(product_id)})
          if not product_data or not product_data.get("embedding"):
               return []
          
          results = await self.vector_search_products(
               query_embedding=product_data["embedding"],
               limit=limit + 1
          )
          
          return [r for r in results if str(r["_id"]) != product_id][:limit]