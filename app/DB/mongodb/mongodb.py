from app.config.settings import settings
from motor.motor_asyncio import AsyncIOMotorClient
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
     
     async def init_indexes(self):
          """Initialize database indexes - call this on app startup"""
          await self.user_collection.create_index("user_id", unique=True)
          await self.session_collection.create_index([("session_id", 1), ("user_id", 1)], unique=True)
          await self.message_collection.create_index([("session_id", 1), ("timestamp", 1)])
          await self.message_collection.create_index("user_id")
          await self.workout_collection.create_index("user_id")
          await self.meal_collection.create_index("user_id")
          await self.meal_collection.create_index([("date", 1), ("user_id", 1)], unique=True)
          await self.workout_collection.create_index([("date", 1), ("user_id", 1)], unique=True)

     async def get_sessions(self, user_id: str) -> List[Dict]:
          """Get all sessions for a user"""
          cursor = self.session_collection.find(
               {"user_id": user_id},
               {"_id": 0, "session_id": 1, "title": 1, "created_at": 1, "updated_at": 1}
          ).sort("updated_at", -1)
          return await cursor.to_list(length=100)
     
     async def get_messages(self, session_id: str) -> List[Dict]:
          """Get all messages for a session"""
          cursor = self.message_collection.find(
               {"session_id": session_id},
               {"_id": 0, "content": 1, "role": 1, "timestamp": 1, "image_url": 1}
          ).sort("timestamp", 1)
          return await cursor.to_list(length=1000)
     
     async def create_session(self, user_id: str, session_id: str, title: str = "New Conversation"):
          """Create a new session"""
          session_doc = {
               "user_id": user_id,
               "session_id": session_id,
               "title": title,
               "created_at": datetime.utcnow(),
               "updated_at": datetime.utcnow()
          }
          try:
               await self.session_collection.insert_one(session_doc)
               return session_doc
          except Exception as e:
               # Session might already exist, update it instead
               await self.update_session(session_id, title)
               return session_doc
     
     async def update_session(self, session_id: str, title: Optional[str] = None):
          """Update session title and/or updated_at timestamp"""
          update_doc = {"updated_at": datetime.utcnow()}
          if title:
               update_doc["title"] = title
          
          await self.session_collection.update_one(
               {"session_id": session_id},
               {"$set": update_doc}
          )
     
     async def save_message(
          self, 
          session_id: str, 
          user_id: str,
          role: str, 
          content: str,
          image_url: Optional[str] = None
     ):
          """Save a single message (user or assistant)"""
          message_doc = {
               "session_id": session_id,
               "user_id": user_id,
               "role": role,  # "user" or "assistant"
               "content": content,
               "timestamp": datetime.utcnow()
          }
          
          if image_url:
               message_doc["image_url"] = image_url
          
          await self.message_collection.insert_one(message_doc)
          
          # Update session's updated_at timestamp
          await self.update_session(session_id)
     
     async def save_conversation_turn(
          self,
          session_id: str,
          user_id: str,
          user_message: str,
          assistant_message: str,
          user_image_url: Optional[str] = None,
          assistant_image_url: Optional[str] = None
     ):
          """Save both user message and assistant response in one go"""
          # Save user message
          await self.save_message(
               session_id=session_id,
               user_id=user_id,
               role="user",
               content=user_message,
               image_url=user_image_url
          )
          
          # Save assistant message
          await self.save_message(
               session_id=session_id,
               user_id=user_id,
               role="assistant",
               content=assistant_message,
               image_url=assistant_image_url
          )
     
     async def delete_session(self, session_id: str, user_id: str):
          """Delete a session and all its messages"""
          await self.session_collection.delete_one({
               "session_id": session_id,
               "user_id": user_id
          })
          await self.message_collection.delete_many({
               "session_id": session_id,
               "user_id": user_id
          })
     
     
     async def get_meal(self, user_id: str):
          """Get all meals for a user"""
          cursor = await self.meal_collection.find(
               {"user_id": user_id},
               {"meal": 1},
               sort=["created_at", -1],
               limit=3
          )
          return await cursor.to_list(length=3)
     async def get_workout(self, user_id: str):
          """Get all workouts for a user"""
          cursor = await self.workout_collection.find(
               {"user_id": user_id},
               {"workout": 1},
               sort=["created_at", -1],
               limit=3
          )
          return await cursor.to_list(length=3)