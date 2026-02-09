from openai import AsyncOpenAI
from app.config.settings import settings
from app.DB.mongodb.mongodb import MongoDB
from app.prompt.prompt import Workout_system_prompt,Workout_user_prompt
from .daily_workout_schema import WorkoutSession


class DailyWorkout:
     def __init__(self):
          self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
          self.db = MongoDB()

     async def get_prompt(self,user_id:str):
          workout = await self.db.get_workout(user_id)
          personal_setup = await self.db.get_personal_setup(user_id)
          if not workout:
               workout="not found previous 3 days workouts"
               personal_setup="not found personal setup"
          system_prompt = Workout_system_prompt.format(workout_schema=WorkoutSession.model_json_schema())
          user_prompt = Workout_user_prompt.format(personal_setup=personal_setup,past_3_days_workouts=workout)
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
               return WorkoutSession.model_validate_json(response)     
          except Exception as e:
               return e