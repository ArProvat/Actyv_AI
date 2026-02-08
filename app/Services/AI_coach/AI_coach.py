from app.utils.file_handler.file_handler import FileHandler
from app.config.settings import settings
from app.modules.graph.builder import graph_builder
from app.DB.mongodb.mongodb import MongoDB
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient
import base64
import json
import uuid


class AI_coach:
     def __init__(self):
          self.file_handler = FileHandler()
          self.client = MongoClient(settings.DATABASE_URL)
          self.checkpointer = MongoDBSaver(self.client)
          self.graph = graph_builder().compile(checkpointer=self.checkpointer)
          self.db = MongoDB()

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
          # Generate session_id if not provided
          if not session_id:
               session_id = str(uuid.uuid4())
          
          if not user_id:
               user_id = "anonymous"
          
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
                    "thread_id": session_id,
                    "user_id": user_id
               }
          }
          
          # Variables to track the conversation
          full_response = []
          generated_image_url = None
          generated_title = None
          has_yielded_text = False
          has_yielded_image = False
          has_yielded_title = False
          
          try:
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
                              full_response.append(chunk.content)
                              yield {
                                   "type": "text",
                                   "content": chunk.content
                              }
                    
                    # Handle node completions
                    elif kind == "on_chain_end":
                         output = event.get("data", {}).get("output", {})
                         
                         # Check if this is one of our conversation nodes
                         if name in ["conversation_node", "conversation_node_with_image"]:
                              # If there's an image, yield it
                              if "generated_image" in output and not has_yielded_image:
                                   has_yielded_image = True
                                   generated_image_url = output["generated_image"]
                                   yield {
                                        "type": "image",
                                        "content": generated_image_url
                                   }
                         
                         # Handle title generation
                         elif name == "generate_title":
                              if "title" in output and not has_yielded_title:
                                   has_yielded_title = True
                                   generated_title = output["title"]
                                   yield {
                                        "type": "title",
                                        "content": generated_title
                                   }
               
               # After streaming completes, save to database
               assistant_response = "".join(full_response)
               
               # If we didn't stream anything, get the final state
               if not has_yielded_text:
                    final_state = await self.graph.aget_state(config)
                    if final_state and final_state.values.get("messages"):
                         last_message = final_state.values["messages"][-1]
                         if isinstance(last_message, AIMessage):
                              assistant_response = last_message.content
                              yield {
                                   "type": "text",
                                   "content": assistant_response
                              }
                         
                         # Check for image in final state
                         if final_state.values.get("generated_image") and not has_yielded_image:
                              generated_image_url = final_state.values["generated_image"]
                              yield {
                                   "type": "image",
                                   "content": generated_image_url
                              }
                         
                         # Check for title in final state
                         if final_state.values.get("title") and not has_yielded_title:
                              generated_title = final_state.values["title"]
                              yield {
                                   "type": "title",
                                   "content": generated_title
                              }
               
               # Save the conversation to MongoDB
               if assistant_response:
                    # Create or update session with title if generated
                    if generated_title:
                         await self.db.create_session(
                              user_id=user_id,
                              session_id=session_id,
                              title=generated_title
                         )
                    
                    # Save the conversation turn
                    await self.db.save_conversation_turn(
                         session_id=session_id,
                         user_id=user_id,
                         user_message=query,  # Original query text
                         assistant_message=assistant_response,
                         user_image_url= None,
                         assistant_image_url=generated_image_url
                    )
          
          except Exception as e:
               yield {
                    "type": "error",
                    "content": f"Error in graph execution: {str(e)}"
               }
     
     async def get_chat_history(self, session_id: str):
          """Retrieve chat history for a session"""
          return await self.db.get_messages(session_id)
     
     async def get_user_sessions(self, user_id: str):
          """Retrieve all sessions for a user"""
          return await self.db.get_sessions(user_id)
     
     async def delete_session(self, session_id: str, user_id: str):
          """Delete a session"""
          await self.db.delete_session(session_id, user_id)