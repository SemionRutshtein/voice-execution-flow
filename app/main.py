import logging
import uuid
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse

from .config import settings
from .database import connect_to_mongo, close_mongo_connection, create_voice_action, get_voice_actions_by_user, get_voice_action_by_id
from .models import VoiceActionCreate, VoiceActionResponse
from .audio_processor import audio_processor

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    logger.info("Application started")
    yield
    # Shutdown
    await close_mongo_connection()
    logger.info("Application shutdown")


app = FastAPI(
    title="Banking Voice Action API",
    description="API for processing banking voice actions",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main application page"""
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Banking Voice Action App</h1><p>Frontend not found. Please check static files.</p>",
            status_code=404
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Banking Voice Action API is running"}


@app.post("/api/upload-audio", response_model=VoiceActionResponse)
async def upload_audio(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None)
):
    """
    Upload and process audio file for banking action
    """
    try:
        # Generate user ID if not provided
        if not user_id:
            user_id = str(uuid.uuid4())
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size
        content = await file.read()
        if len(content) > settings.MAX_AUDIO_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.MAX_AUDIO_FILE_SIZE} bytes"
            )
        
        # Check file type
        allowed_types = ['audio/wav', 'audio/mpeg', 'audio/mp4', 'audio/ogg', 'audio/webm']
        if file.content_type not in allowed_types:
            logger.warning(f"Unexpected content type: {file.content_type}, proceeding anyway")
        
        logger.info(f"Processing audio file: {file.filename} for user: {user_id}")
        
        # Process audio
        transcription, processed_filename = await audio_processor.process_audio_file(
            content, file.filename
        )
        
        # Create voice action record
        voice_action = VoiceActionCreate(
            userId=user_id,
            audioTranscript=transcription,
            audioFileName=processed_filename
        )
        
        # Save to database
        created_action = await create_voice_action(voice_action)
        
        # Return response
        return VoiceActionResponse(
            id=str(created_action.id),
            userId=created_action.userId,
            audioTranscript=created_action.audioTranscript,
            audioFileName=created_action.audioFileName,
            processed=created_action.processed,
            timestamp=created_action.timestamp
        )
        
    except Exception as e:
        logger.error(f"Error processing audio upload: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")


@app.get("/api/user/{user_id}/actions", response_model=List[VoiceActionResponse])
async def get_user_actions(user_id: str, limit: int = 100):
    """
    Get all voice actions for a specific user
    """
    try:
        actions = await get_voice_actions_by_user(user_id, limit)
        
        return [
            VoiceActionResponse(
                id=str(action.id),
                userId=action.userId,
                audioTranscript=action.audioTranscript,
                audioFileName=action.audioFileName,
                processed=action.processed,
                timestamp=action.timestamp
            )
            for action in actions
        ]
        
    except Exception as e:
        logger.error(f"Error fetching user actions: {e}")
        raise HTTPException(status_code=500, detail="Error fetching user actions")


@app.get("/api/action/{action_id}", response_model=VoiceActionResponse)
async def get_action(action_id: str):
    """
    Get a specific voice action by ID
    """
    try:
        action = await get_voice_action_by_id(action_id)
        
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")
        
        return VoiceActionResponse(
            id=str(action.id),
            userId=action.userId,
            audioTranscript=action.audioTranscript,
            audioFileName=action.audioFileName,
            processed=action.processed,
            timestamp=action.timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching action: {e}")
        raise HTTPException(status_code=500, detail="Error fetching action")


@app.post("/api/generate-session")
async def generate_session():
    """
    Generate a new session ID for a user
    """
    return {"userId": str(uuid.uuid4())}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )