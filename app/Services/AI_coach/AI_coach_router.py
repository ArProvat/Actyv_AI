from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import json
from .AI_coach import AI_coach
from app.modules.auth.auth import verify_token
from fastapi.encoders import jsonable_encoder


router = APIRouter()
ai_coach = AI_coach()


class ChatResponse(BaseModel):
     type: str
     content: str


'''@router.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
     """
     Chat endpoint without file upload
     
     Request body:
          {
               "query": "Hello, I need help with my workout",
               "user_id": "user123",
               "session_id": "session456"
          }
     """
     async def event_stream():
          try:
               async for chunk in ai_coach.get_response(
                    query=request.query,
                    user_id=request.user_id,
                    session_id=request.session_id
               ):
                    # Send as Server-Sent Events format
                    yield f"data: {json.dumps(chunk)}\n\n"
          except Exception as e:
               error_chunk = {"type": "error", "content": str(e)}
               yield f"data: {json.dumps(error_chunk)}\n\n"
     
     return StreamingResponse(
          event_stream(),
          media_type="text/event-stream",
          headers={
               "Cache-Control": "no-cache",
               "Connection": "keep-alive",
          }
     )
'''


@router.post("/api/chat")
async def chat_with_file_endpoint(
     query: str = Form(...),
     file: Optional[UploadFile] = File(None),
     session_id: Optional[str] = Form(None),
     user: Depends(verify_token)
):
     """
     Chat endpoint with optional file upload

     Form data:
          - query: User's message
          - file: Optional uploaded file
          - user_id: User identifier (required for saving)
          - session_id: Session identifier (auto-generated if not provided)

     Returns streaming response with text and optionally images
     """
     file_bytes = None
     file_extension = None
     user_id = user["user_id"]
     if file:
          file_bytes = await file.read()
          if file.filename:
               file_extension = file.filename.split(".")[-1].lower()

     async def event_stream():
          try:
               async for chunk in ai_coach.get_response(
                    query=query,
                    file=file_bytes,
                    file_extension=file_extension,
                    user_id=user_id,
                    session_id=session_id,
               ):
                    yield f"data: {json.dumps(chunk)}\n\n"
          except Exception as e:
               error_chunk = {"type": "error", "content": str(e)}
               yield f"data: {json.dumps(error_chunk)}\n\n"

     return StreamingResponse(
          event_stream(),
          media_type="text/event-stream",
          headers={
               "Cache-Control": "no-cache",
               "Connection": "keep-alive",
          },
     )


@router.get("/api/sessions")
async def get_user_sessions(user: Depends(verify_token)):
     """
     Get all sessions for a user

     Returns:
          List of sessions with session_id, title, created_at, updated_at
     """
     user_id = user["user_id"]
     try:
          sessions = await ai_coach.get_user_sessions(user_id)
          return JSONResponse(
               content={"success": True, "sessions": jsonable_encoder(sessions)}
          )
     except Exception as e:
          return JSONResponse(
               status_code=500, content={"success": False, "error": str(e)}
          )


@router.get("/api/messages/{session_id}")
async def get_session_messages(session_id: str, user: Depends(verify_token)):
     """
     Get all messages for a session

     Returns:
          List of messages with role, content, timestamp
     """
     user_id = user["user_id"]
     try:
          messages = await ai_coach.get_chat_history(session_id, user_id)
          return JSONResponse(
               content={"success": True, "messages": jsonable_encoder(messages)}
          )
     except Exception as e:
          return JSONResponse(
               status_code=500, content={"success": False, "error": str(e)}
          )


@router.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, user: Depends(verify_token)):
     """
     Delete a session and all its messages

     Form data:
          - user_id: User identifier for authorization
     """
     user_id = user["user_id"]
     try:
          await ai_coach.delete_session(session_id, user_id)
          return JSONResponse(
               content={"success": True, "message": "Session deleted successfully"}
          )
     except Exception as e:
          return JSONResponse(
               status_code=500, content={"success": False, "error": str(e)}
          )


@router.get("/api/health")
async def health_check():
     """Health check endpoint"""
     return {"status": "healthy", "service": "AI Coach API"}
