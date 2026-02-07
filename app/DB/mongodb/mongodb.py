from app.config.settings import settings
from motor.motor_asyncio import AsyncIOMotorClient

class MongoDB:
     def __init__(self):
          self.client = AsyncIOMotorClient(settings.DATABASE_URL)
          self.db = self.client[settings.DATABASE_NAME]
          self.user_collection = self.db["users"]
          self.session_collection = self.db["sessions"]
          self.message_collection = self.db["messages"]
          self.init_indexes()
     
     def init_indexes(self):
          self.user_collection.create_index("user_id", unique=True)
          self.session_collection.create_index([("session_id", 1), ("user_id", 1)], unique=True)
          self.message_collection.create_index([("session_id", 1), ("user_id", 1)], unique=True)


     async def get_session(self, user_id: str):
          return await self.session_collection.find(
               {"user_id": user_id},
               {"_id": 0, "session_id": 1, "created_at": 1, "updated_at": 1}
          )
     
     async def get_message(self, session_id: str):
          return await self.message_collection.find(
               {"session_id": session_id},
               {"content": 1, "role": 1, "timestamp": 1},
               sort=[("timestamp", 1)]
          )
     
     async def save_session(self, user_id: str,session_id: str):
          return await self.session_collection.insert_one({"user_id": user_id, "session_id": session_id})
     
     async def save_message(self session_id: str, role: str, content: str):
          return await self.message_collection.insert_one({"session_id": session_id, "role": role, "content": content})