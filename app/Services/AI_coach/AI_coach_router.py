from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
from app.modules.ai_coach import AI_coach



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
     user_id: Optional[str] = Form(None),
     session_id: Optional[str] = Form(None)
):
     """
     Chat endpoint with optional file upload
     
     Form data:
          - query: User's message
          - file: Optional uploaded file
          - user_id: User identifier
          - session_id: Session identifier
     
     Returns streaming response with text and optionally images
     """
     file_bytes = None
     file_extension = None
     
     if file:
          file_bytes = await file.read()
          if file.filename:
               file_extension = file.filename.split('.')[-1].lower()
     
     async def event_stream():
          try:
               async for chunk in ai_coach.get_response(
                    query=query,
                    file=file_bytes,
                    file_extension=file_extension,
                    user_id=user_id,
                    session_id=session_id
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
          }
     )


@router.get("/api/health")
async def health_check():
     """Health check endpoint"""
     return {"status": "healthy", "service": "AI Coach API"}

