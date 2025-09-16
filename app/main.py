import logging
import uuid
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from .config import settings
from .models import N8NProcessingResult
from .language_detector import language_detector
from .n8n_service import n8n_service

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application started")
    yield
    # Shutdown
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


@app.post("/api/process-voice")
async def process_voice_message(
    audio: UploadFile = File(...),
    userId: Optional[str] = Form(None)
):
    """
    Process voice message with language detection and send to N8N webhook
    """
    try:
        # Generate user ID if not provided
        if not userId:
            userId = str(uuid.uuid4())

        # Validate file
        if not audio.filename:
            raise HTTPException(status_code=400, detail="No audio file provided")

        # Check file size
        content = await audio.read()
        if len(content) > settings.MAX_AUDIO_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.MAX_AUDIO_FILE_SIZE} bytes"
            )

        logger.info(f"Processing voice message for user: {userId}")

        # Detect language from audio
        detected_language = await language_detector.detect_language_from_audio(content, audio.filename)

        # Send language and MP3 data to N8N webhook
        n8n_result = await n8n_service.process_voice_with_language(
            user_id=userId,
            language=detected_language,
            voice_record=content,
            filename=audio.filename
        )

        # Return response with N8N result
        return {
            "success": True,
            "userId": userId,
            "detectedLanguage": detected_language,
            "filename": audio.filename,
            "n8nResult": {
                "success": n8n_result.success,
                "result": n8n_result.result,
                "error": n8n_result.error,
                "processingTime": n8n_result.processingTime
            }
        }

    except Exception as e:
        logger.error(f"Error processing voice message: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing voice message: {str(e)}")


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