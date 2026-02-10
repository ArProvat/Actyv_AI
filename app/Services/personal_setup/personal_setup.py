
from app.DB.mongodb.mongodb import MongoDB
from openai import AsyncOpenAI
from fastapi import HTTPException
from app.config.settings import settings


class personalSetup:
     def __init__(self):
          self.mongodb = MongoDB()
          self.personal_collection = self.mongodb.personal_collection
          self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
     
     async def create_personal_setup(self, user_id: str, personal_setup: UserSetup):
          try:
               personal_setup_dict = personal_setup.dict()
               personal_setup_dict["user_id"] = user_id
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
     
     async def update_personal_setup(self, user_id: str, personal_setup: UserSetup):
          try:
               personal_setup_dict = personal_setup.dict()
               result = await self.personal_collection.update_one({"user_id": user_id}, {"$set": personal_setup_dict})
               
               return result.modified_count
          except Exception as e:
               raise HTTPException(status_code=400, detail=str(e))
     
     async def get_prompt(self):



     async def get_response(self, user_id: str, personal_setup: dict):
          try:
               result = await self.personal_collection.find_one({"user_id": user_id})

               system_prompt ,user_prompt = await self.get_prompt()
               
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
