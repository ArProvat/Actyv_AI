from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from app.config.settings import settings
from app.prompt.prompt import IMAGE_SCENARIO_PROMPT
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate


class Scenario(BaseModel):
     narrative: str = Field(..., description="The AI's narrative response to the question")
     image_prompt: str = Field(..., description="The visual prompt to generate an image")


class TextToImage:
     def __init__(self):
          self.image_llm = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
          self.small_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

     async def get_image(self, messageHistory: list):
          narrative, image_prompt = await self.get_image_prompt(messageHistory)

          response = await self.image_llm.images.generate(
               model="dall-e-3",           # ✅ valid model
               prompt=image_prompt,
               size="1024x1024",
               quality="standard",
               n=1,
               response_format="url",      # ✅ supported by dall-e-3
          )
          return response.data[0].url

     async def get_image_prompt(self, messageHistory: list):
          formatted_chat_history = "\n".join(
               [f"{message.type}: {message.content}" for message in messageHistory]  # ✅ .type not .role
          )

          prompt = PromptTemplate.from_template(IMAGE_SCENARIO_PROMPT)  # ✅ string, not dict
          llm = self.small_llm.with_structured_output(Scenario)
          chain = prompt | llm

          response = await chain.ainvoke({"chat_history": formatted_chat_history})  # ✅ await
          return response.narrative, response.image_prompt