import os
import tempfile
import logging
from pathlib import Path
from typing import Optional, Tuple
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import which

from .config import settings

logger = logging.getLogger(__name__)

# Set up pydub to use ffmpeg if available
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffmpeg = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

# Ensure FLAC is available for speech recognition
flac_path = which("flac")
if flac_path:
    logger.info(f"FLAC utility found at: {flac_path}")
else:
    logger.warning("FLAC utility not found in PATH")


class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.temp_dir = Path(settings.TEMP_AUDIO_DIR)
        self.temp_dir.mkdir(exist_ok=True)
    
    async def process_audio_file(self, audio_content: bytes, filename: str) -> Tuple[str, str]:
        """
        Process audio file and return transcription
        
        Args:
            audio_content: Raw audio file content
            filename: Original filename
            
        Returns:
            Tuple of (transcription_text, processed_filename)
        """
        temp_file_path = None
        processed_file_path = None
        
        try:
            # Save uploaded file temporarily
            temp_file_path = self._save_temp_file(audio_content, filename)
            
            # Convert to WAV if needed
            processed_file_path = await self._convert_to_wav(temp_file_path)
            
            # Transcribe audio
            transcription = await self._transcribe_audio(processed_file_path)
            
            return transcription, processed_file_path.name
            
        except Exception as e:
            logger.error(f"Error processing audio file {filename}: {e}")
            raise
        finally:
            # Clean up temporary files
            self._cleanup_file(temp_file_path)
            if processed_file_path and processed_file_path != temp_file_path:
                # Keep processed file for a short time in case it's needed
                pass
    
    def _save_temp_file(self, content: bytes, filename: str) -> Path:
        """Save uploaded content to temporary file"""
        suffix = Path(filename).suffix or '.tmp'
        
        with tempfile.NamedTemporaryFile(
            delete=False,
            dir=self.temp_dir,
            suffix=suffix
        ) as temp_file:
            temp_file.write(content)
            return Path(temp_file.name)
    
    async def _convert_to_wav(self, input_path: Path) -> Path:
        """Convert audio file to WAV format"""
        try:
            # If already WAV, return as is
            if input_path.suffix.lower() == '.wav':
                return input_path
            
            # Load and convert to WAV
            audio = AudioSegment.from_file(str(input_path))
            
            # Create output path
            output_path = input_path.with_suffix('.wav')
            
            # Export as WAV
            audio.export(str(output_path), format="wav")
            
            logger.info(f"Converted {input_path.name} to {output_path.name}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting audio file: {e}")
            # If conversion fails, try to proceed with original file
            return input_path
    
    async def _transcribe_audio(self, audio_path: Path) -> str:
        """Transcribe audio file to text"""
        try:
            # Try to load the audio file
            with sr.AudioFile(str(audio_path)) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Record the audio
                audio = self.recognizer.record(source)
                
                # Transcribe using Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                
                logger.info(f"Successfully transcribed audio: {text[:100]}...")
                return text
                
        except sr.UnknownValueError:
            logger.warning("Speech recognition could not understand audio")
            return "Could not understand audio clearly. Please try speaking more clearly or checking your microphone."
        except sr.RequestError as e:
            logger.error(f"Could not request results from speech recognition service: {e}")
            return f"Speech recognition service error. Please check your internet connection."
        except FileNotFoundError as e:
            logger.error(f"Audio file not found: {e}")
            return "Audio file processing error. Please try recording again."
        except Exception as e:
            error_msg = str(e)
            if "FLAC conversion utility not available" in error_msg:
                logger.error(f"FLAC conversion error: {e}")
                # Try to convert to FLAC manually using pydub and ffmpeg
                return await self._try_flac_fallback(audio_path)
            else:
                logger.error(f"Unexpected error during transcription: {e}")
                return f"Transcription error: {error_msg}"
    
    async def _try_flac_fallback(self, audio_path: Path) -> str:
        """Fallback method when FLAC utility is not available"""
        try:
            # Convert to FLAC using pydub/ffmpeg
            logger.info("Trying FLAC fallback conversion...")
            audio = AudioSegment.from_wav(str(audio_path))
            
            # Create FLAC file
            flac_path = audio_path.with_suffix('.flac')
            audio.export(str(flac_path), format="flac")
            
            logger.info(f"Converted to FLAC: {flac_path}")
            
            # Try transcription again with FLAC file
            with sr.AudioFile(str(flac_path)) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                
                logger.info(f"Successfully transcribed using FLAC fallback: {text[:100]}...")
                
                # Clean up FLAC file
                self._cleanup_file(flac_path)
                
                return text
                
        except Exception as fallback_error:
            logger.error(f"FLAC fallback also failed: {fallback_error}")
            return "Audio conversion error. Unable to process audio format. Please try recording in WAV format."
    
    def _cleanup_file(self, file_path: Optional[Path]) -> None:
        """Remove temporary file"""
        if file_path and file_path.exists():
            try:
                file_path.unlink()
                logger.debug(f"Cleaned up file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not remove file {file_path}: {e}")
    
    async def cleanup_old_files(self, max_age_hours: int = 24) -> None:
        """Clean up old temporary files"""
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for file_path in self.temp_dir.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    self._cleanup_file(file_path)


# Global instance
audio_processor = AudioProcessor()