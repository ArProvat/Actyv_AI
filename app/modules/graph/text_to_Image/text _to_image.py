
from pydantic import BaseModel
from openai import AsyncOpenAI
from app.config.settings import settings
from app.prompt.prompt import IMAGE_SCENARIO_PROMPT
from app.modules.graph.state import GraphState
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig

class senario(BaseModel):
     """Class for the scenario response"""

     narrative: str = Field(..., description="The AI's narrative response to the question")
     image_prompt: str = Field(..., description="The visual prompt to generate an image representing the scene")

class TextToImage:
     def __init__(self):
          self.image_llm = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
          self.small_llm = ChatOpenAI(model="gpt-4o-mini",temperature=0.2)
     
     async def get_image(self,messageHistory:list):
          narrative,image_prompt = await self.get_image_prompt(messageHistory)

          response = await self.image_llm.images.generate(
                    model="gpt-image-1-mini",
                    prompt=image_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                    response_format="url"
          )
          image_url = response.data[0].url
          #img_response = requests.get(image_url)
          #image_bytes = BytesIO(img_response.content)
          #s3_manager = S3_Manager()
          #image_url = await s3_manager.upload_file_from_bytes(image_bytes)
          return image_url
          


          
     async def get_image_prompt(self,messageHistory:list):
          formate_chat_history = "\n".join([f"{message.role}: {message.content}" for message in messageHistory])
          prompt = PromptTemplate.from_template(
               {
                    "input_variables":["chat_history"],
                    "template":IMAGE_SCENARIO_PROMPT
                    
               }
          )
          llm = self.small_llm.with_structured_output(senario)
          chain = prompt | llm
          response = chain.invoke({"chat_history":formate_chat_history})
          return response.narrative,response.image_prompt
          

