from app.utils.file_handler.file_handler import FileHandler
from app.config.settings import settings
from app.modules.graph.builder import graph_builder
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient
import base64
import json


class AI_coach:
     def __init__(self):
          self.file_handler = FileHandler()
          self.client = MongoClient(settings.DATABASE_URL)
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
          
          try:
               # Track which node we're in and what we've yielded
               current_node = None
               has_yielded_text = False
               has_yielded_image = False
               has_yielded_title = False
               
               # Use astream_events for granular streaming
               async for event in self.graph.astream_events(
                    {"messages": [message]},
                    config=config,
                    version="v2"
               ):
                    kind = event.get("event")
                    name = event.get("name", "")
                    
                    # Stream text chunks from LLM
                    if kind == "on_chat_model_stream":
                         chunk = event.get("data", {}).get("chunk")
                         if chunk and hasattr(chunk, 'content') and chunk.content:
                              has_yielded_text = True
                              yield {
                                   "type": "text",
                                   "content": chunk.content
                              }
                    
                    # Handle node completions
                    elif kind == "on_chain_end":
                         # Check if this is one of our conversation nodes
                         if name in ["conversation_node", "conversation_node_with_image"]:
                              output = event.get("data", {}).get("output", {})
                              
                              # If there's an image, yield it
                              if "generated_image" in output and not has_yielded_image:
                                   has_yielded_image = True
                                   yield {
                                        "type": "image",
                                        "content": output["generated_image"]
                                   }
                         
                         # Handle title generation
                         elif name == "generate_title":
                              output = event.get("data", {}).get("output", {})
                              if "title" in output and not has_yielded_title:
                                   has_yielded_title = True
                                   yield {
                                        "type": "title",
                                        "content": output["title"]
                                   }
               
               # If we didn't stream anything (edge case), get the final state
               if not has_yielded_text:
                    final_state = await self.graph.aget_state(config)
                    if final_state and final_state.values.get("messages"):
                         last_message = final_state.values["messages"][-1]
                         if isinstance(last_message, AIMessage):
                              yield {
                                   "type": "text",
                                   "content": last_message.content
                              }
                         
                         # Check for image in final state
                         if final_state.values.get("generated_image") and not has_yielded_image:
                              yield {
                                   "type": "image",
                                   "content": final_state.values["generated_image"]
                              }
          
          except Exception as e:
               yield {
                    "type": "error",
                    "content": f"Error in graph execution: {str(e)}"
               }