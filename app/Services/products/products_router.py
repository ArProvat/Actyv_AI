from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.Services.products.products import ProductService
from app.Services.products.products_schema import Product

router = APIRouter()
service = ProductService()


@router.post("/products/", response_model=Product)
async def create_product(product_data: dict):
    """Create a new product with embedding"""
    try:
        result = service.create_product_with_embedding(product_data)
        return {"message": "Product created successfully", "product": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/products/{product_id}")
async def update_product(product_id: str, product_data: dict):
    """Update a product with embedding"""
    try:
        result = await service.update_product_with_embedding(product_id, product_data)
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": "Product updated successfully", "product": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/search")
async def search_products(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_rating: Optional[float] = None,
):
    """Search products using vector similarity"""
    try:
        filters = {}
        if category:
            filters["category"] = category
        if min_price is not None or max_price is not None:
            filters["price_range"] = {
                "min": min_price or 0,
                "max": max_price or float("inf"),
            }
        if min_rating:
            filters["min_rating"] = min_rating

        results = service.search_by_text_query(query, limit, filters)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{product_id}/similar")
async def get_similar_products(product_id: str, limit: int = 5):
    """Get similar products"""
    try:
        results = service.get_similar_products(product_id, limit)
        if not results:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"similar_products": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
