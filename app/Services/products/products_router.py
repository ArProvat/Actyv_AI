from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from app.Services.products.products import ProductService

router = APIRouter()

@router.get("/search")
async def search_products(
     query: str = Query(..., description="Search query"),
     user_id: str = Query(..., description="User ID for personalization"),
     limit: int = Query(10, ge=1, le=50),
     category: Optional[str] = None,
     min_price: Optional[float] = None,
     max_price: Optional[float] = None,
     min_rating: Optional[float] = None,
     use_personalization: bool = Query(True, description="Enable personalized results"),
     service: ProductService = Depends()
):
     """
     Enhanced personalized search endpoint
     
     - **query**: What the user is searching for
     - **user_id**: User ID to personalize results
     - **use_personalization**: Toggle personalization on/off
     """
     
     filters = {}
     if category:
          filters['category'] = category
     if min_price is not None or max_price is not None:
          filters['price_range'] = {
               'min': min_price or 0,
               'max': max_price or float('inf')
          }
     if min_rating:
          filters['min_rating'] = min_rating
     
     results = await service.search_by_text_query(
          user_id=user_id,
          query=query,
          limit=limit,
          filters=filters if filters else None,
          use_personalization=use_personalization
     )
     
     return {
          "query": query,
          "personalized": use_personalization,
          "count": len(results),
          "results": results
     }

@router.get("/{product_id}/similar")
async def get_similar_products(
     product_id: str,
     limit: int = Query(5, ge=1, le=20),
     service: ProductService = Depends()
     ):
     """Get products similar to the given product"""
     
     similar = await service.get_similar_products(
          product_id=product_id,
          limit=limit
     )
     
     return {
          "product_id": product_id,
          "count": len(similar),
          "similar_products": similar
     }

@router.post("/interactions")
async def log_interaction(
     user_id: str,
     product_id: str,
     interaction_type: str,
     service: ProductService = Depends()
     ):
     """
     Log user-product interaction
     
     Types: view, click, purchase, add_to_cart
     """
     
     await service.log_product_interaction(
          user_id=user_id,
          product_id=product_id,
          interaction_type=interaction_type
     )
     
     return {"status": "logged"}