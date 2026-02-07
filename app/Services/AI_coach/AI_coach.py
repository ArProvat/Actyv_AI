
from app.utils.file_handler.file_handler import FileHandler
from app.config.settings import settings
from app.modules.graph.builder import graph_builder
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.mongodb import MongoDBSaver
from motor.motor_asyncio import AsyncIOMotorClient
import base64
import json


class AI_coach:
     def __init__(self):
          self.file_handler = FileHandler()
          self.client = AsyncIOMotorClient(settings.MONGO_URI)
          self.checkpointer = MongoDBSaver(self.client)
          self.graph = graph_builder().compile(checkpointer=self.checkpointer)

     async def get_response(
          self,
          query: str,
          file: bytes | None = None,
          file_extension: str | None = None,
          user_id: str | None = None,
          session_id: str | None = None
          ):
          """
          Stream responses from the AI coach using LangGraph streaming
          """
          message_content = query
          
          # Handle file if provided
          if file and file_extension:
               if file_extension.lower() in ['jpg', 'png', 'jpeg', 'webp']:
                    message_content = [
                         {"type": "text", "text": query},
                         {
                         "type": "image_url",
                         "image_url": {
                              "url": f"data:image/{file_extension};base64,{base64.b64encode(file).decode('utf-8')}"
                         }
                         }
                    ]
               else:
                    file_text = await self.file_handler.file_handler(file, f'.{file_extension}')
                    if file_text and not file_text.startswith("Error") and not file_text.startswith("Unsupported"):
                         message_content = f"{file_text}\n\n{query}"
          
          
          message = HumanMessage(content=message_content)
          
          config = {
               "configurable": {
                    "thread_id": session_id or "default",
                    "user_id": user_id or "default"
               }
          }
                    has_streamed = False
          
          try:
                    async for event in self.graph.astream_events(
                    {"messages": [message]},
                    config=config,
                    version="v2"
               ):
                    kind = event.get("event")
                    
                    if kind == "on_chat_model_stream":
                         chunk = event.get("data", {}).get("chunk")
                         if chunk and hasattr(chunk, 'content') and chunk.content:
                         has_streamed = True
                         yield {
                              "type": "text",
                              "content": chunk.content
                         }
                         if chunk.type == "title":
                              yield {
                                   "type": "title",
                                   "content": chunk.content
                              }
                    
                    elif kind == "on_chain_end":
                         node_name = event.get("name", "")
                         
                         if node_name == "conversation_with_image":
                         output = event.get("data", {}).get("output", {})
                         if "generated_image" in output:
                              yield {
                                   "type": "image",
                                   "content": output["generated_image"]
                              }
               
               if not has_streamed:
                    final_state = await self.graph.aget_state(config)
                    if final_state and final_state.values.get("messages"):
                         last_message = final_state.values["messages"][-1]
                         if isinstance(last_message, AIMessage):
                         yield {
                              "type": "text",
                              "content": last_message.content
                         }
          
          except Exception as e:
               yield {
                    "type": "error",
                    "content": f"Error in graph execution: {str(e)}"
               }

     async def get_response_simple(
          self,
          query: str,
          file: bytes | None = None,
          file_extension: str | None = None,
          user_id: str | None = None,
          session_id: str | None = None
     ):
          """
          Simpler streaming approach using node updates
          """
          message_content = query
          
          # Handle file
          if file and file_extension:
               if file_extension.lower() in ['jpg', 'png', 'jpeg', 'webp']:
                    message_content = [
                         {"type": "text", "text": query},
                         {
                         "type": "image_url",
                         "image_url": {
                              "url": f"data:image/{file_extension};base64,{base64.b64encode(file).decode('utf-8')}"
                         }
                         }
                    ]
               else:
                    file_text = await self.file_handler.file_handler(file, f'.{file_extension}')
                    if file_text and not file_text.startswith("Error"):
                         message_content = f"{file_text}\n\n{query}"
          
          message = HumanMessage(content=message_content)
          
          config = {
               "configurable": {
                    "thread_id": session_id or "default",
                    "user_id": user_id or "default"
               }
          }
          
          try:
               async for chunk in self.graph.astream(
                    {"messages": [message]},
                    config=config,
                    stream_mode="values"
               ):
                    if "messages" in chunk and chunk["messages"]:
                         last_msg = chunk["messages"][-1]
                         if isinstance(last_msg, AIMessage):
                         yield {
                              "type": "text",
                              "content": last_msg.content
                         }
                    
                    if "generated_image" in chunk:
                         yield {
                         "type": "image",
                         "content": chunk["generated_image"]
                         }
          
          except Exception as e:
               yield {
                    "type": "error",
                    "content": f"Error: {str(e)}"
               }