"""
Speech-to-text client using free services.
"""
import speech_recognition as sr
import requests
import base64
import logging
from typing import Dict, Any, Optional
import io
import os
from pydub import AudioSegment
from pydub.playback import play

logger = logging.getLogger(__name__)

class SpeechToTextClient:
    """Client for free speech-to-text services."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.supported_formats = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']

    def transcribe_audio_file(self, audio_file_path: str, language: str = 'en-US') -> Dict[str, Any]:
        """Transcribe audio file to text using free services."""
        try:
            # Convert audio to WAV format if needed
            wav_path = self._convert_to_wav(audio_file_path)

            # Try multiple free services
            results = []

            # Try Google Speech Recognition (free tier)
            google_result = self._transcribe_with_google(wav_path, language)
            if google_result["success"]:
                results.append(("google", google_result))

            # Try with SpeechRecognition library (offline)
            offline_result = self._transcribe_offline(wav_path)
            if offline_result["success"]:
                results.append(("offline", offline_result))

            # Return best result
            if results:
                best_service, best_result = results[0]  # Prefer first successful one
                return {
                    "success": True,
                    "transcription": best_result["transcription"],
                    "confidence": best_result.get("confidence", 0.8),
                    "service_used": best_service,
                    "language": language
                }
            else:
                return {
                    "success": False,
                    "error": "All transcription services failed",
                    "transcription": ""
                }

        except Exception as e:
            logger.error(f"Error in audio transcription: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcription": ""
            }

    def _convert_to_wav(self, audio_file_path: str) -> str:
        """Convert audio file to WAV format."""
        try:
            file_ext = os.path.splitext(audio_file_path)[1].lower()

            if file_ext == '.wav':
                return audio_file_path

            # Convert using pydub
            if file_ext == '.mp3':
                audio = AudioSegment.from_mp3(audio_file_path)
            elif file_ext == '.m4a':
                audio = AudioSegment.from_file(audio_file_path, "m4a")
            elif file_ext == '.ogg':
                audio = AudioSegment.from_ogg(audio_file_path)
            elif file_ext == '.flac':
                audio = AudioSegment.from_file(audio_file_path, "flac")
            else:
                raise ValueError(f"Unsupported audio format: {file_ext}")

            # Export as WAV
            wav_path = audio_file_path.replace(file_ext, '.wav')
            audio.export(wav_path, format="wav")
            return wav_path

        except Exception as e:
            logger.error(f"Error converting audio: {e}")
            raise

    def _transcribe_with_google(self, wav_path: str, language: str) -> Dict[str, Any]:
        """Transcribe using Google Speech Recognition (free tier)."""
        try:
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio_data = self.recognizer.record(source)

            # Use Google Speech Recognition (free tier)
            text = self.recognizer.recognize_google(audio_data, language=language)

            return {
                "success": True,
                "transcription": text,
                "confidence": 0.85  # Estimated confidence
            }

        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
            return {"success": False, "error": "Could not understand audio"}
        except sr.RequestError as e:
            logger.error(f"Google Speech Recognition error: {e}")
            return {"success": False, "error": f"Service error: {e}"}

    def _transcribe_offline(self, wav_path: str) -> Dict[str, Any]:
        """Transcribe using offline recognition (if available)."""
        try:
            with sr.AudioFile(wav_path) as source:
                audio_data = self.recognizer.record(source)

            # Try offline recognition (requires additional setup)
            try:
                text = self.recognizer.recognize_sphinx(audio_data)
                return {
                    "success": True,
                    "transcription": text,
                    "confidence": 0.7  # Lower confidence for offline
                }
            except sr.UnknownValueError:
                return {"success": False, "error": "Offline recognition could not understand audio"}
            except sr.RequestError:
                # Sphinx not installed
                return {"success": False, "error": "Offline recognition not available"}

        except Exception as e:
            logger.error(f"Offline transcription error: {e}")
            return {"success": False, "error": str(e)}

    def validate_audio_file(self, file_path: str) -> Dict[str, Any]:
        """Validate audio file format and properties."""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext not in self.supported_formats:
                return {
                    "valid": False,
                    "error": f"Unsupported format: {file_ext}",
                    "supported_formats": self.supported_formats
                }

            # Check file size (limit to 10MB for free tiers)
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 10MB
                return {
                    "valid": False,
                    "error": "File too large (max 10MB)",
                    "size": file_size
                }

            # Try to load audio to check validity
            try:
                if file_ext == '.wav':
                    with sr.AudioFile(file_path) as source:
                        duration = source.DURATION
                elif file_ext == '.mp3':
                    audio = AudioSegment.from_mp3(file_path)
                    duration = len(audio) / 1000.0  # Convert to seconds
                else:
                    audio = AudioSegment.from_file(file_path)
                    duration = len(audio) / 1000.0

                return {
                    "valid": True,
                    "duration": duration,
                    "size": file_size,
                    "format": file_ext
                }

            except Exception as e:
                return {
                    "valid": False,
                    "error": f"Invalid audio file: {e}"
                }

        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
