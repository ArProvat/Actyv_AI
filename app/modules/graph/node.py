from app.config.settings import settings
from app.prompt.prompt import ROUTER_PROMPT , IMAGE_SCENARIO_PROMPT
from app.modules.graph.state import GraphState
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig
class Node:
     def __init__(self):
          self.llm = ChatOpenAI(model="gpt-4.1-mini",temperature=0.3)
          self.small_llm = ChatOpenAI(model="gpt-3.5-turbo",temperature=0.2)
     
     def router_node(self,state:GraphState):

          prompt = ChatPromptTemplate.from_template(
               {
                    "system":ROUTER_PROMPT,
                    MessagesPlaceholder(variable_name="messages")
                    
               }
          )

          chain = prompt | self.small_llm 
          response = chain.invoke({"messages":state["messages"][-3:]})
          return {"workflow":response.workflow}


     def conversation_node(self,state:GraphState,config:RunnableConfig):
          prompt = ChatPromptTemplate.from_template(
               {
                    "system":CONVERSATION_PROMPT,
                    MessagesPlaceholder(variable_name="messages")
                    
               }
          )
          chain = prompt | self.llm 
          for chunk,metadata in chain.stream({"messages":state["messages"][-20:],
                                   "personal_setup":state["personal_setup"],
                                   "summary":state["summary"]},
                                   config,
                                   stream_mode="messages"
                                   ):
                                        yield chunk.content

     def conversation_node_with_image(self,state:GraphState,config:RunnableConfig):
          
          
          prompt = ChatPromptTemplate.from_template(
               {
                    "system":IMAGE_SCENARIO_PROMPT,
                    MessagesPlaceholder(variable_name="messages")
                    
               }
          )
          chain = prompt | self.llm 
          for chunk,metadata in chain.stream({"messages":state["messages"][-20:],
                                   "personal_setup":state["personal_setup"],
                                   "summary":state["summary"]},
                                   config,
                                   stream_mode="messages"
                                   ):
                                        yield chunk.content


          
