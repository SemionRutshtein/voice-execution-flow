import httpx
import time
import logging
from typing import Optional, Dict, Any

from .config import settings
from .models import N8NProcessingResult

logger = logging.getLogger(__name__)


class N8NService:
    def __init__(self):
        self.webhook_url = settings.N8N_WEBHOOK_URL
        self.timeout = settings.N8N_TIMEOUT

    async def process_voice_message(self, user_id: str, transcript: str, audio_filename: Optional[str] = None) -> N8NProcessingResult:
        """Send voice message to n8n workflow for processing"""
        start_time = time.time()

        payload = {
            "userId": user_id,
            "transcript": transcript,
            "audioFileName": audio_filename,
            "timestamp": time.time()
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Sending request to n8n webhook: {self.webhook_url}")
                logger.debug(f"Payload: {payload}")

                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )

                processing_time = time.time() - start_time

                if response.status_code == 200:
                    result_data = response.json()
                    logger.info(f"n8n processing completed successfully in {processing_time:.2f}s")

                    return N8NProcessingResult(
                        success=True,
                        result=result_data,
                        processingTime=processing_time
                    )
                else:
                    error_msg = f"n8n webhook returned status {response.status_code}: {response.text}"
                    logger.error(error_msg)

                    return N8NProcessingResult(
                        success=False,
                        error=error_msg,
                        processingTime=processing_time
                    )

        except httpx.TimeoutException:
            processing_time = time.time() - start_time
            error_msg = f"n8n webhook timeout after {self.timeout}s"
            logger.error(error_msg)

            return N8NProcessingResult(
                success=False,
                error=error_msg,
                processingTime=processing_time
            )

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Error calling n8n webhook: {str(e)}"
            logger.error(error_msg)

            return N8NProcessingResult(
                success=False,
                error=error_msg,
                processingTime=processing_time
            )

    async def process_voice_audio(self, user_id: str, audio_content: bytes, audio_filename: str) -> N8NProcessingResult:
        """Send audio file to N8N workflow for AI processing (voice-to-text and AI response)"""
        start_time = time.time()

        try:
            # Create multipart form data for audio file
            files = {
                "audio": (audio_filename, audio_content, "audio/webm")
            }

            data = {
                "userId": user_id,
                "timestamp": str(time.time())
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Sending audio to N8N AI webhook: {self.webhook_url}")
                logger.debug(f"User: {user_id}, Filename: {audio_filename}")

                response = await client.post(
                    self.webhook_url,
                    files=files,
                    data=data
                )

                processing_time = time.time() - start_time

                if response.status_code == 200:
                    result_data = response.json()
                    logger.info(f"N8N AI processing completed successfully in {processing_time:.2f}s")

                    return N8NProcessingResult(
                        success=True,
                        result=result_data,
                        processingTime=processing_time
                    )
                elif response.status_code == 404:
                    # N8N workflow not configured - provide fallback response
                    logger.warning("N8N workflow not configured (404). Providing fallback response.")
                    fallback_result = {
                        "transcript": "Voice recorded successfully",
                        "aiResponse": "Hello! I'm your banking assistant. The N8N workflow is not yet configured. Please set up the workflow in N8N at http://localhost:5678 to enable AI processing with OpenAI.",
                        "userId": user_id,
                        "timestamp": time.time(),
                        "success": True,
                        "fallback": True
                    }

                    return N8NProcessingResult(
                        success=True,
                        result=fallback_result,
                        processingTime=processing_time
                    )
                else:
                    error_msg = f"N8N AI webhook returned status {response.status_code}: {response.text}"
                    logger.error(error_msg)

                    return N8NProcessingResult(
                        success=False,
                        error=error_msg,
                        processingTime=processing_time
                    )

        except httpx.TimeoutException:
            processing_time = time.time() - start_time
            error_msg = f"N8N AI webhook timeout after {self.timeout}s"
            logger.error(error_msg)

            return N8NProcessingResult(
                success=False,
                error=error_msg,
                processingTime=processing_time
            )

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Error calling N8N AI webhook: {str(e)}"
            logger.error(error_msg)

            return N8NProcessingResult(
                success=False,
                error=error_msg,
                processingTime=processing_time
            )


# Global instance
n8n_service = N8NService()