
from app.DB.mongodb.mongodb import MongoDB
from openai import AsyncOpenAI
from fastapi import HTTPException
from app.config.settings import settings
from app.prompt.prompt import personal_setup_user_prompt, personal_setup_system_prompt
from .personal_setup_schema import StrategyRoadmap
from app.utils.embedding.embedding import LocalEmbeddingService

class personalSetup:
     def __init__(self):
          self.mongodb = MongoDB()
          self.personal_collection = self.mongodb.personal_collection
          self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
          self.embedding_service = LocalEmbeddingService()
     
     async def create_personal_setup(self, user_id: str, personal_setup: dict):
          try:
               personal_setup_dict = personal_setup
               personal_setup_dict["user_id"] = user_id
               personal_setup_dict["embedding"] = await self.embedding_service.generate_embedding(personal_setup_dict)
               result = await self.personal_collection.insert_one(personal_setup_dict)
               return result._id
          except Exception as e:
               raise HTTPException(status_code=400, detail=str(e))
     
     async def get_personal_setup(self, user_id: str):
          try:
               result = await self.personal_collection.find_one({"user_id": user_id})
               return result
          except Exception as e:
               raise HTTPException(status_code=400, detail=str(e))
     
     async def update_personal_setup(self, user_id: str, personal_setup: dict):
          try:
               personal_setup_dict = personal_setup
               personal_setup_dict["user_id"] = user_id
               personal_setup_dict["embedding"] = await self.embedding_service.generate_embedding(personal_setup_dict)
               result = await self.personal_collection.update_one({"user_id": user_id}, {"$set": personal_setup_dict})
               
               return result.modified_count
          except Exception as e:
               raise HTTPException(status_code=400, detail=str(e))
     
     async def get_prompt(self, new_personal_setup: dict):
          system_prompt = personal_setup_system_prompt.format(plan_schema=StrategyRoadmap.schema_json())
          user_prompt = personal_setup_user_prompt.format(personal_setup=new_personal_setup)
          return system_prompt, user_prompt


     async def get_response(self, user_id: str, new_personal_setup: dict):
          try:
               existing_personal_setup = await self.personal_collection.find_one({"user_id": user_id})
               if existing_personal_setup:
                    await self.update_personal_setup(user_id, new_personal_setup)
               else:
                    await self.create_personal_setup(user_id, new_personal_setup)
               system_prompt ,user_prompt = await self.get_prompt(new_personal_setup)
               
               completions = await self.openai.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                         {"role": "system", "content": system_prompt},
                         {"role": "user", "content": user_prompt}
                    ]
               )
               response = completions.choices[0].message.content
               if response.startswith("```json"):
                    response = response[7:]
               if response.endswith("```"):
                    response = response[:-3]
               
               return response
          except Exception as e:
               raise HTTPException(status_code=400, detail=str(e))
