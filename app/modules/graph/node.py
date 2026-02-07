from app.config.settings import settings
from app.prompt.prompt import ROUTER_PROMPT, IMAGE_SCENARIO_PROMPT, CONVERSATION_PROMPT
from app.modules.graph.state import GraphState
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, RemoveMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from .text_to_image import TextToImage  


class Node:
     def __init__(self):
          self.llm = ChatOpenAI(model="gpt-5-mini", temperature=0.3)
          self.small_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
          self.image_node = TextToImage()
     
     async def router_node(self, state: GraphState):
          """Route to appropriate conversation node"""
          prompt = ChatPromptTemplate.from_messages([
               ("system", ROUTER_PROMPT),
               MessagesPlaceholder(variable_name="messages")
          ])

          chain = prompt | self.small_llm | StrOutputParser()
          response = await chain.ainvoke({"messages": state["messages"][-3:]})
          
          # Clean up the response and map 'image' to 'conversation_with_image'
          workflow = response.strip().lower()
          if workflow == "image":
               workflow = "conversation_with_image"
          elif workflow != "conversation":
               # Default to conversation if response is unexpected
               workflow = "conversation"
     
          return {"workflow": workflow}

     async def personal_setup_node(self, state: GraphState, config: RunnableConfig):
          """Fetch user's personal setup/preferences"""
          user_id = config.get("configurable", {}).get("user_id")
          # TODO: Fetch from database based on user_id
          return {"personal_setup": "want to do gym notion else want to do "}

     async def conversation_node(self, state: GraphState, config: RunnableConfig):
          """Handle conversation responses - RETURNS state update"""
          # Format the system prompt with context
          system_message = CONVERSATION_PROMPT.format(
               personal_setup=state.get("personal_setup", "No personal setup available"),
               summary=state.get("summary", "No previous conversation summary")
          )
          
          prompt = ChatPromptTemplate.from_messages([
               ("system", system_message),
               MessagesPlaceholder(variable_name="messages")
          ])
          
          chain = prompt | self.llm
          
          # Invoke to get complete response
          response = await chain.ainvoke({
               "messages": state["messages"][-20:]
          })
          
          # Return the complete message for state update
          return {'messages': [AIMessage(content=response.content)]}

     async def conversation_node_with_image(self, state: GraphState, config: RunnableConfig):
          """Handle conversation responses with image generation - RETURNS state update"""
          # Generate image first
          image_url = await self.image_node.get_image(state["messages"][-3:])
          
          # Format the system prompt with context
          system_message = CONVERSATION_PROMPT.format(
               personal_setup=state.get("personal_setup", "No personal setup available"),
               summary=state.get("summary", "No previous conversation summary")
          )
          
          prompt = ChatPromptTemplate.from_messages([
               ("system", system_message),
               MessagesPlaceholder(variable_name="messages")
          ])
          
          chain = prompt | self.llm
          
          # Invoke to get complete response
          response = await chain.ainvoke({
               "messages": state["messages"][-20:]
          })
          
          # Return both message and image
          return {
               'messages': [AIMessage(content=response.content)],
               'generated_image': image_url
          }

     async def summary_node(self, state: GraphState, config: RunnableConfig):
          """Summarize conversation when it gets too long"""
          if len(state['messages']) > 20:
               if state.get('summary'):
                    summary_message = (
                         f"This is summary of the conversation to date between Ava and the user: {state['summary']}\n\n"
                         "Extend the summary by taking into account the new messages above:"
                    )
               else:
                    summary_message = (
                         "Create a summary of the conversation above between Ava and the user. "
                         "The summary must be a short description of the conversation so far, "
                         "but that captures all the relevant information shared between Ava and the user:"
                    )

               messages = state['messages'] + [HumanMessage(content=summary_message)]
               response = await self.small_llm.ainvoke(messages)
               summary = response.content

               # Keep only the last 5 messages
               delete_messages = [RemoveMessage(id=m.id) for m in state['messages'][:-5]]
               return {'summary': summary, 'messages': delete_messages}
          
          return {}

     async def generate_title(self, state: GraphState, config: RunnableConfig):
          """Generate title for the conversation"""
          if state.get('title'):
               return {}
          
          prompt = ChatPromptTemplate.from_messages([
               ("system", "Generate a title for the conversation base on the message in 6-8 words"),
               ("user", "{message}")
          ])
          
          chain = prompt | self.small_llm | StrOutputParser()
          title = await chain.ainvoke({"message": state["messages"][-1].content})
          
          return {"title": title}