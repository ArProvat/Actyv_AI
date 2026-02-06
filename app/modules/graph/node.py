from app.config.settings import settings
from app.prompt.prompt import ROUTER_PROMPT , IMAGE_SCENARIO_PROMPT
from app.modules.graph.state import GraphState
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage,AIMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig
from .text_to_Image.text_to_image import TextToImage
class Node:
     def __init__(self):
          self.llm = ChatOpenAI(model="gpt-5-mini",temperature=0.3)
          self.small_llm = ChatOpenAI(model="gpt-4o-mini",temperature=0.2)
     
     async def router_node(self,state:GraphState):

          prompt = ChatPromptTemplate.from_template(
               {
                    "system":ROUTER_PROMPT,
                    MessagesPlaceholder(variable_name="messages")
                    
               }
          )

          chain = prompt | self.small_llm 
          response = chain.invoke({"messages":state["messages"][-3:]})
          return {"workflow":response.workflow}
     async def  peronal_setup_node(self,state:GraphState,config:RunnableConfig):
          user_id = config.configurable.get("user_id")
          return {"personal_setup":"want to do gym notion else want to do "}

     async def conversation_node(self,state:GraphState,config:RunnableConfig):
          prompt = ChatPromptTemplate.from_template(
               {
                    "system":CONVERSATION_PROMPT,
                    MessagesPlaceholder(variable_name="messages")
                    
               }
          )
          chain = prompt | self.llm 
          full_response = []
          for chunk,metadata in chain.stream({"messages":state["messages"][-20:],
                                   "personal_setup":state["personal_setup"],
                                   "summary":state["summary"]},
                                   config,
                                   stream_mode="messages"
                                   ):
               full_response.append(chunk)
               yield {'type':'text','content':chunk.content}
          return {'messages':AIMessage(content="".join([chunk.content for chunk in full_response]))}
     async def conversation_node_with_image(self,state:GraphState,config:RunnableConfig):
          
          image_node = TextToImage()
          image = await image_node.get_image(state["messages"][-3:])
          
          prompt = ChatPromptTemplate.from_template(
               {
                    "system":CONVERSATION_PROMPT,
                    MessagesPlaceholder(variable_name="messages")
                    
               }
          )
          chain = prompt | self.llm 
          full_response = []
          for chunk,metadata in chain.stream({"messages":state["messages"][-20:],
                                   "personal_setup":state["personal_setup"],
                                   "summary":state["summary"]},
                                   config,
                                   stream_mode="messages"
                                   ):
               full_response.append(chunk)
               yield {'type':'text','content':chunk.content}
          yield {'type':'image','content':image}
          return {'messages':AIMessage(content="".join([chunk.content for chunk in full_response])) }


