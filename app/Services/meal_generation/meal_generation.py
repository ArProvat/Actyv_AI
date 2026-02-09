from openai import AsyncOpenAI
from app. config.settings import settings
from .meal_generation_schema import DailyMealLog
from app.prompt.prompt import Meal_system_prompt,Meal_user_prompt
from app.DB.mongodb.mongodb import MongoDB


class MealGeneration:
     def __init__(self):
          self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
          self.db = MongoDB()
     
     async def get_prompt(self,user_id:str):
          meal = await self.db.get_meal(user_id)
          workout = await self.db.get_workout(user_id)
          if not meal or not workout:
               meal="not found previous 3 days meals"
               workout="not found previous 3 days workouts"
          system_prompt = Meal_system_prompt.format(workout_schema=DailyMealLog.model_json_schema())
          user_prompt = Meal_user_prompt.format(meals=meal,workouts=workout)
          return system_prompt,user_prompt
     
     async def get_response(self,user_id:str):
          try:
               system_prompt,user_prompt = await self.get_prompt(user_id)
               completions = await self.client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[
                         {"role": "system", "content": system_prompt},
                         {"role": "user", "content": user_prompt}
                    ]
               )
               response = completions.choices[0].message.content
               if response.startswith("```json"):
                    response = response[7:-3]
               print(response)
               return DailyMealLog.model_validate_json(response)     
          except Exception as e:
               return e