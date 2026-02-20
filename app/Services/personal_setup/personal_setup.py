
from requests import request
from app.DB.mongodb.mongodb import MongoDB
from openai import AsyncOpenAI
from fastapi import HTTPException
from app.config.settings import settings
from .personal_setup_schema import StrategyRoadmap
from app.utils.embedding.embedding import LocalEmbeddingService
from bson import ObjectId
from bson.errors import InvalidId
from app.prompt.prompt import initial_planning_system_prompt, initial_planning_user_prompt
import json
from datetime import datetime, timezone
import httpx

class personalSetup:
     def __init__(self):
          self.mongodb = MongoDB()
          self.personal_collection = self.mongodb.personal_setup_collection
          self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
          self.embedding_service = LocalEmbeddingService()
     

     async def create_personal_setup(self, userId: str, personal_setup: dict):
          try:
               now = datetime.now(timezone.utc) # Use UTC for consistency
               personal_setup_dict = personal_setup
               
               personal_setup_dict["userId"] = ObjectId(userId)
               # Add timestamps here
               personal_setup_dict["createdAt"] = now
               personal_setup_dict["updatedAt"] = now
               
               result = await self.personal_collection.insert_one(personal_setup_dict)
               return str(result.inserted_id) # Return as string to avoid the ObjectId error we discussed earlier
          except Exception as e:
               raise HTTPException(status_code=400, detail=str(e))
     async def get_personal_setup(self, userId: str):
          try:
               # 1. Convert string to ObjectId for the query
               oid = ObjectId(userId)
               
               result = await self.personal_collection.find_one({"userId": oid})
               
               if result:
                    result["_id"] = str(result["_id"])
                    if isinstance(result.get("userId"), ObjectId):
                         result["userId"] = str(result["userId"])
                         
               return result
          except InvalidId:
               raise HTTPException(status_code=400, detail="Invalid ID format")
          except Exception as e:
               raise HTTPException(status_code=500, detail=str(e))
     async def update_personal_setup(self, userId: str, personal_setup: dict):
          try:
               personal_setup["updatedAt"] = datetime.now(timezone.utc)
               result = await self.personal_collection.update_one(
                    {"userId": ObjectId(userId)}, {"$set": personal_setup}
               )
               if result.matched_count == 0:
                    raise HTTPException(status_code=404, detail="User setup not found")
               return {
                    "matched": result.matched_count,
                    "modified": result.modified_count,
                    "message": "Updated" if result.modified_count > 0 else "No changes detected"
               }
          except HTTPException:
               raise
          except Exception as e:
               raise HTTPException(status_code=500, detail=str(e)) 
     
     async def get_prompt(self, personal_setup: dict):
          schema_dict = StrategyRoadmap.model_json_schema()
          schema_json = json.dumps(schema_dict, indent=2)
          schema_escaped = schema_json.replace("{", "{{").replace("}", "}}")
          system_prompt = initial_planning_system_prompt.format(plan_schema=schema_escaped)
          user_prompt = initial_planning_user_prompt.format(personal_setup=personal_setup)
          return system_prompt, user_prompt

     async def get_response(self, userId: str, new_personal_setup: dict):
          try:
               existing_personal_setup = await self.personal_collection.find_one({"userId": ObjectId(userId)})
               
               if existing_personal_setup:
                    update_result = await self.update_personal_setup(userId, new_personal_setup)
                    print(f"Update result: {update_result}")
               else:
                    insert_id = await self.create_personal_setup(userId, new_personal_setup)
                    print(f"Created new setup: {insert_id}")
                    url = f"http://72.62.160.245:5555/api/v1/users/generate-daily-workout-and-nutrition"
                    try:
                         async with httpx.AsyncClient() as client:
                              await client.post(url, json={"userId": insert_id})
                    except Exception as e:
                         print(f"❌ Failed to generate daily workout and nutrition: {e}")
               system_prompt, user_prompt = await self.get_prompt(new_personal_setup)
               
               completions = await self.openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                         {"role": "system", "content": system_prompt},
                         {"role": "user", "content": user_prompt}
                    ]
               )
               
               response = completions.choices[0].message.content
               
               # Strip markdown
               response = response.strip()
               if response.startswith("```json"):
                    response = response[7:].lstrip()
               elif response.startswith("```"):
                    response = response[3:].lstrip()
               if response.endswith("```"):
                    response = response[:-3].rstrip()
               response = response.strip()
               
               try:
                    strategy_roadmap_dict = json.loads(response)
               except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse JSON response: {e}")
                    raise HTTPException(status_code=500, detail=f"Invalid JSON from AI: {str(e)}")
               
               await self.update_personal_setup(userId, {"strategy_roadmap": strategy_roadmap_dict})
               
               return {
                    "message": "Personal setup updated successfully",
                    "response": strategy_roadmap_dict  
               }
          
          except HTTPException:
               raise
          except Exception as e:
               print(f"❌ Error in get_response: {type(e).__name__}: {str(e)}")
               raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")
