from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
     @classmethod
     def __get_validators__(cls):
          yield cls.validate

     @classmethod
     def validate(cls, v):
          if not ObjectId.is_valid(v):
               raise ValueError("Invalid ObjectId")
          return ObjectId(v)

     @classmethod
     def __get_pydantic_json_schema__(cls, field_schema):
          field_schema.update(type="string")


class ProductCategory(str, Enum):
     SUPPLEMENTS = "SUPPLEMENTS"
     VITAMINS = "VITAMINS"
     PROTEIN = "PROTEIN"
     FITNESS = "FITNESS"
     NUTRITION = "NUTRITION"
     EQUIPMENT = "EQUIPMENT"
     ACCESSORIES = "ACCESSORIES"


class ProductStatus(str, Enum):
     ACTIVE = "ACTIVE"
     INACTIVE = "INACTIVE"
     OUT_OF_STOCK = "OUT_OF_STOCK"


class Product(BaseModel):
     id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
     name: str
     category: ProductCategory = ProductCategory.SUPPLEMENTS
     description: str
     price: int
     discount: int
     stock: int
     total_sales: int = Field(default=0, alias="totalSales")
     features: List[str] = []
     variants: List[str] = []
     image: str
     status: ProductStatus = ProductStatus.ACTIVE
     total_review: int = Field(default=0, alias="totalReview")
     average_rating: float = Field(default=0.0, alias="averageRating")
     vendor_id: PyObjectId = Field(alias="vendorId")
     user_id: Optional[PyObjectId] = Field(default=None, alias="userId")

     embedding: Optional[List[float]] = None

     created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
     updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")

     class Config:
          populate_by_name = True
          arbitrary_types_allowed = True
          json_encoders = {ObjectId: str}


