from app.config.settings import settings
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

from datetime import datetime
from typing import List, Dict, Optional


class MongoDB:
     def __init__(self):
          self.client = AsyncIOMotorClient(settings.DATABASE_URL)
          self.db = self.client[settings.DATABASE_NAME]
          self.user_collection = self.db["users"]
          self.session_collection = self.db["sessions"]
          self.message_collection = self.db["messages"]
          self.workout_collection = self.db["workouts"]
          self.meal_collection = self.db["meals"]
          # FIX: Standardized naming
          self.personal_setup_collection = self.db["personalSetup"]
          self.product_collection = self.db["products"]
     async def init_indexes(self):
          """Initialize database indexes - call this on app startup"""
          # Session indexes
          await self.session_collection.create_index([("session_id", 1), ("userId", 1)], unique=True)
          
          # Message indexes
          await self.message_collection.create_index([("session_id", 1), ("timestamp", 1)])
          await self.message_collection.create_index("userId")
          
          # User Specific indexes
          await self.personal_setup_collection.create_index("userId")
          
          # Product indexes
          await self.product_collection.create_index("vendor_id")
          await self.product_collection.create_index("category")
          await self.product_collection.create_index("status")
          
          # Meal & Workout Unique Daily indexes
          await self.meal_collection.create_index([("date", 1), ("userId", 1)], unique=True)
          await self.workout_collection.create_index([("date", 1), ("userId", 1)], unique=True)
          
          # Vector search initialization
          try:
               await self.create_vector_search_index(self.product_collection)
          except Exception as e:
               print(f"Search index skip/error: {e}")


     async def create_vector_search_index(self, collection):
          """Create vector search index for products collection"""
          
          # The structure requires 'type': 'vectorSearch' and 'fields' 
          # to be defined explicitly for Atlas Vector Search.
          index_definition = {
               "fields": [
                    {
                         "type": "vector",
                         "path": "embedding",
                         "numDimensions":384,
                         "similarity": "cosine"
                    },
                    {
                         "type": "filter",
                         "path": "category"
                    },
                    {
                         "type": "filter",
                         "path": "status"
                    }
               ]
          }
          
          try:
               # Use the explicit search index model
               await collection.create_search_index(
                    model={
                         "name": "product_vector_index",
                         "type": "vectorSearch",
                         "definition": index_definition
                    }
               )
               print("Vector search index creation initiated!")
          except Exception as e:
               if "already exists" in str(e):
                    print("Vector search index already exists.")
               else:
                    print(f"Failed to create search index: {e}")
     async def get_sessions(self, userId: str) -> List[Dict]:
          cursor = self.session_collection.find(
               {"userId": userId},                          # ✅ plain string
               {"_id": 0, "session_id": 1, "title": 1, "created_at": 1, "updated_at": 1}
          ).sort("updated_at", -1)
          return await cursor.to_list(length=100)

     async def get_messages(self, session_id: str, user_id: str) -> List[Dict]:
          cursor = self.message_collection.find(
               {"session_id": session_id, "userId": user_id},                  # ✅ plain string
               {"_id": 0, "content": 1, "role": 1, "timestamp": 1, "image_url": 1}
          ).sort("timestamp", 1)
          return await cursor.to_list(length=1000)

     async def create_session(self, userId: str, session_id: str, title: str = "New Conversation"):
          session_doc = {
               "userId": userId,                            # ✅ plain string
               "session_id": session_id,                    # ✅ plain string
               "title": title,
               "created_at": datetime.utcnow(),
               "updated_at": datetime.utcnow()
          }
          try:
               await self.session_collection.insert_one(session_doc)
               return session_doc
          except Exception as e:
               await self.update_session(session_id, title)
               return session_doc

     async def update_session(self, session_id: str, title: Optional[str] = None):
          update_doc = {"updated_at": datetime.utcnow()}
          if title:
               update_doc["title"] = title
          await self.session_collection.update_one(
               {"session_id": session_id},                  # ✅ plain string
               {"$set": update_doc}
          )

     async def save_message(
          self,
          session_id: str,
          userId: str,
          role: str,
          content: str,
          image_url: Optional[str] = None
          ):
          message_doc = {
               "session_id": session_id,                    # ✅ plain string
               "userId": userId,                            # ✅ plain string
               "role": role,
               "content": content,
               "timestamp": datetime.utcnow()
          }
          if image_url:
               message_doc["image_url"] = image_url

          await self.message_collection.insert_one(message_doc)
          await self.update_session(session_id)

     async def save_conversation_turn(
          self,
          session_id: str,
          userId: str,
          user_message: str,
          assistant_message: str,
          user_image_url: Optional[str] = None,
          assistant_image_url: Optional[str] = None
          ):
          await self.save_message(
               session_id=session_id,                       # ✅ plain string
               userId=userId,                               # ✅ plain string
               role="user",
               content=user_message,
               image_url=user_image_url
          )
          await self.save_message(
               session_id=session_id,                       # ✅ plain string
               userId=userId,                               # ✅ plain string
               role="assistant",
               content=assistant_message,
               image_url=assistant_image_url
          )

     async def delete_session(self, session_id: str, userId: str):
          await self.session_collection.delete_one({
               "session_id": session_id,                    # ✅ plain string
               "userId": userId                             # ✅ plain string
          })
          await self.message_collection.delete_many({
               "session_id": session_id,                    # ✅ plain string
               "userId": userId                             # ✅ plain string
          })
     
     async def get_meal(self, userId: str):
          cursor = self.meal_collection.find(
               {"userId": ObjectId(userId)},
               {"meals": 1}
          ).sort("created_at", -1).limit(3)
          return await cursor.to_list(length=3)

     async def get_workout(self, userId: str):
          cursor = self.workout_collection.find(
               {"userId": ObjectId(userId)},
               {"workoutCategories": 1}
          ).sort("created_at", -1).limit(3)
          return await cursor.to_list(length=3)

     async def get_personal_setup(self, userId: str):
          cursor = self.personal_setup_collection.find(
               {"userId": ObjectId(userId)},
               {"personal_setup": 1}
          ).sort("created_at", -1).limit(1)
          return await cursor.to_list(length=1)

     async def get_strategy_roadmap(self, userId: str):
          cursor = self.personal_setup_collection.find(
               {"userId": ObjectId(userId)},
               {"strategy_roadmap": 1}
          ).sort("created_at", -1).limit(1)
          return await cursor.to_list(length=1)