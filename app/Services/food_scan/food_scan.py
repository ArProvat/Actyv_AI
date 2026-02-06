
from openai import AsyncOpenAI
from app.prompt.prompt import food_scan_system_prompt, food_scan_user_prompt
from app.config.settings import settings
from .food_scan_schema import FoodScanResponse
from fastapi import HTTPException
import json
import base64

class food_scan_service:
     def __init__(self):
          self.client = AsyncOpenAI(
          api_key=settings.OPENAI_API_KEY
          )
     
     async def generate_response(self,food_image: bytes) -> str:
          try:
               System_prompt = food_scan_system_prompt.format(structure_output=FoodScanResponse.model_json_schema())

               completion = await self.client.chat.completions.create(
                    model="gpt-4.1-mini",
                    temperature=0.2,
                    messages=[
                         {"role": "system", "content": System_prompt},
                         {"role": "user", "content":[
                         {'type':'text','text':food_scan_user_prompt},
                         {'type':'image_url','image_url':{'url':f'data:image/jpeg;base64,{base64.b64encode(food_image).decode("utf-8")}'}}
                         ]}

                    ]
               )

               response = completion.choices[0].message.content
               if response.startswith('```json'):
                    response = response[7:]
               if response.endswith('```'):
                    response = response[:-3]
               return FoodScanResponse(**json.loads(response))
          except Exception as e:
               raise HTTPException(status_code=500, detail=str(e))

