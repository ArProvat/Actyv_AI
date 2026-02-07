from app.config.settings import settings
from app.prompt.prompt import ROUTER_PROMPT, IMAGE_SCENARIO_PROMPT, CONVERSATION_PROMPT
from app.modules.graph.state import GraphState
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, RemoveMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from .text_to_Image.text_to_image import TextToImage

class Node:
     def __init__(self):
          self.llm = ChatOpenAI(model="gpt-5-mini", temperature=0.3)
          self.small_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

     async def router_node(self, state: GraphState):
          """Route to appropriate conversation node"""
          prompt = ChatPromptTemplate.from_messages([
               ("system", ROUTER_PROMPT),
               MessagesPlaceholder(variable_name="messages")
          ])

          chain = prompt | self.small_llm | StrOutputParser()
          response = await chain.ainvoke({"messages": state["messages"][-3:]})
     
          # Expecting response like "conversation" or "conversation_with_image"
          return {"workflow": response.strip()}

     async def personal_setup_node(self, state: GraphState, config: RunnableConfig):
          """Fetch user's personal setup/preferences"""
          user_id = config.get("configurable", {}).get("user_id")
          # TODO: Fetch from database based on user_id
          return {"personal_setup": "want to do gym notion else want to do "}

     async def conversation_node(self, state: GraphState, config: RunnableConfig):
          """Stream conversation responses"""
          prompt = ChatPromptTemplate.from_messages([
               ("system", CONVERSATION_PROMPT),
               MessagesPlaceholder(variable_name="messages")
          ])
          
          chain = prompt | self.llm
          full_response = []
          
          async for chunk in chain.astream({
               "messages": state["messages"][-20:],
               "personal_setup": state.get("personal_setup", ""),
               "summary": state.get("summary", "")
          }):
               if hasattr(chunk, 'content') and chunk.content:
                    full_response.append(chunk.content)
                    yield {'type': 'text', 'content': chunk.content}
          
          # Return the complete message for state update
          return {
               'messages': [AIMessage(content="".join(full_response))]
          }

     async def conversation_node_with_image(self, state: GraphState, config: RunnableConfig):
          """Stream conversation responses with image generation"""
          # Generate image first
          image_node = TextToImage()
          image = await image_node.get_image(state["messages"][-3:])
          
          prompt = ChatPromptTemplate.from_messages([
               ("system", CONVERSATION_PROMPT),
               MessagesPlaceholder(variable_name="messages")
          ])
          
          chain = prompt | self.llm
          full_response = []
          
          async for chunk in chain.astream({
               "messages": state["messages"][-20:],
               "personal_setup": state.get("personal_setup", ""),
               "summary": state.get("summary", "")
          }):
               if hasattr(chunk, 'content') and chunk.content:
                    full_response.append(chunk.content)
                    yield {'type': 'text', 'content': chunk.content}
          
          yield {'type': 'image', 'content': image}
          
          return {
               'messages': [AIMessage(content="".join(full_response))]
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

     async def generate_title(self,state: GraphState, config: RunnableConfig):
          """Generate title for the conversation"""
          if state.get('title'):
               return {}
          prompt = ChatPromptTemplate.from_messages([
               ("system", "Generate a title for the conversation base on the message in 6-8 words"),
               ("user", "{message}")
          ])
          
          chain = prompt | self.small_llm | StrOutputParser()
          title = ""
          for chunk in chain.astream({"message": state["messages"][-1].content}):
               if hasattr(chunk, 'content') and chunk.content:
                    title += chunk.content
                    yield {'type': 'title', 'content': title}
          return {"title": title}