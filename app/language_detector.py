import logging
import tempfile
from pathlib import Path
from typing import Optional
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import which
from langdetect import detect, LangDetectException

from .config import settings

logger = logging.getLogger(__name__)

# Set up pydub to use ffmpeg if available
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffmpeg = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")


class LanguageDetector:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.temp_dir = Path(settings.TEMP_AUDIO_DIR)
        self.temp_dir.mkdir(exist_ok=True)

        # Language code mapping
        self.language_mapping = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'nl': 'Dutch',
            'sv': 'Swedish',
            'no': 'Norwegian',
            'da': 'Danish',
            'fi': 'Finnish',
            'pl': 'Polish',
            'tr': 'Turkish',
            'he': 'Hebrew'
        }

    async def detect_language_from_audio(self, audio_content: bytes, filename: str) -> str:
        """
        Detect language from audio content by transcribing and analyzing text

        Args:
            audio_content: Raw audio file content
            filename: Original filename

        Returns:
            Detected language (full name, e.g., "English", "Spanish")
        """
        temp_file_path = None
        processed_file_path = None

        try:
            # Save uploaded file temporarily
            temp_file_path = self._save_temp_file(audio_content, filename)

            # Convert to WAV if needed
            processed_file_path = await self._convert_to_wav(temp_file_path)

            # Transcribe audio to get text
            transcription = await self._transcribe_audio(processed_file_path)

            if not transcription or transcription.strip() == "":
                logger.warning("No transcription available for language detection")
                return "English"  # Default fallback

            # Detect language from transcribed text
            language = await self._detect_language_from_text(transcription)

            logger.info(f"Detected language: {language} from text: '{transcription[:50]}...'")
            return language

        except Exception as e:
            logger.error(f"Error detecting language from audio: {e}")
            return "English"  # Default fallback
        finally:
            # Clean up temporary files
            self._cleanup_file(temp_file_path)
            if processed_file_path and processed_file_path != temp_file_path:
                self._cleanup_file(processed_file_path)

    async def _detect_language_from_text(self, text: str) -> str:
        """
        Detect language from text using langdetect library

        Args:
            text: Text to analyze

        Returns:
            Detected language name
        """
        try:
            if not text or text.strip() == "":
                return "English"

            # Remove common non-language content that might interfere
            cleaned_text = text.strip()
            if len(cleaned_text) < 3:
                return "English"

            # Use langdetect to identify language
            detected_code = detect(cleaned_text)

            # Convert language code to full name
            language_name = self.language_mapping.get(detected_code, "English")

            logger.info(f"Language detection: '{detected_code}' -> '{language_name}'")
            return language_name

        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}. Using English as default.")
            return "English"
        except Exception as e:
            logger.error(f"Unexpected error in language detection: {e}. Using English as default.")
            return "English"

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

            logger.debug(f"Converted {input_path.name} to {output_path.name}")
            return output_path

        except Exception as e:
            logger.error(f"Error converting audio file: {e}")
            # If conversion fails, try to proceed with original file
            return input_path

    async def _transcribe_audio(self, audio_path: Path) -> str:
        """Transcribe audio file to text for language detection"""
        try:
            # Try to load the audio file
            with sr.AudioFile(str(audio_path)) as source:
                # Adjust for ambient noise briefly
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)

                # Record the audio
                audio = self.recognizer.record(source)

                # Transcribe using Google Speech Recognition
                text = self.recognizer.recognize_google(audio)

                logger.debug(f"Transcribed for language detection: {text[:100]}...")
                return text

        except sr.UnknownValueError:
            logger.warning("Speech recognition could not understand audio for language detection")
            return ""
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error for language detection: {e}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error during transcription for language detection: {e}")
            return ""

    def _cleanup_file(self, file_path: Optional[Path]) -> None:
        """Remove temporary file"""
        if file_path and file_path.exists():
            try:
                file_path.unlink()
                logger.debug(f"Cleaned up file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not remove file {file_path}: {e}")


# Global instance
language_detector = LanguageDetector()