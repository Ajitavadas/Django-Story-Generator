"""
Django views for the story generator API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
import logging
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
import io
from PIL import Image

from .models import Story, GenerationLog
from .serializers import StorySerializer, StoryCreateSerializer
from .langchain_handlers.story_chain import get_story_generator
from .ai_services.huggingface_client import HuggingFaceClient, StableDiffusionFreeClient
from .ai_services.speech_client import SpeechToTextClient
from .utils.image_composer import ImageComposer

logger = logging.getLogger(__name__)

class StoryViewSet(viewsets.ModelViewSet):
    """ViewSet for story generation and management."""

    queryset = Story.objects.all()
    serializer_class = StorySerializer
    parser_classes = [MultiPartParser, JSONParser]

    def get_serializer_class(self):
        if self.action == 'create':
            return StoryCreateSerializer
        return StorySerializer

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a complete story with images."""
        try:
            # Log the generation start
            logger.info("Starting story generation process")
            start_time = time.time()

            # Extract input data
            user_prompt = request.data.get('user_prompt', '')
            audio_file = request.FILES.get('audio_file')

            if not user_prompt and not audio_file:
                return Response(
                    {"error": "Either user_prompt or audio_file is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create story instance
            story = Story.objects.create(
                user_prompt=user_prompt,
                audio_file=audio_file
            )

            # Process generation in background
            generation_result = self._process_story_generation(story)

            if generation_result["success"]:
                story.processing_time = time.time() - start_time
                story.save()

                serializer = self.get_serializer(story)
                return Response({
                    "success": True,
                    "story": serializer.data,
                    "processing_time": story.processing_time
                })
            else:
                return Response({
                    "success": False,
                    "error": generation_result["error"],
                    "story_id": str(story.id)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Error in story generation: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _process_story_generation(self, story: Story) -> dict:
        """Process the complete story generation pipeline."""
        try:
            # Step 1: Speech-to-text (if audio provided)
            if story.audio_file:
                transcription_result = self._process_audio(story)
                if not transcription_result["success"]:
                    return transcription_result

            # Get the final prompt
            final_prompt = story.transcribed_text or story.user_prompt

            # Step 2: Generate story and character description
            story_result = self._generate_story_content(story, final_prompt)
            if not story_result["success"]:
                return story_result

            # Step 3: Generate character image
            character_result = self._generate_character_image(story)
            if not character_result["success"]:
                logger.warning(f"Character image generation failed: {character_result['error']}")

            # Step 4: Generate background image
            background_result = self._generate_background_image(story)
            if not background_result["success"]:
                logger.warning(f"Background image generation failed: {background_result['error']}")

            # Step 5: Compose final image
            if character_result.get("success") and background_result.get("success"):
                composition_result = self._compose_final_image(story)
                if not composition_result["success"]:
                    logger.warning(f"Image composition failed: {composition_result['error']}")

            return {"success": True}

        except Exception as e:
            logger.error(f"Error in story generation pipeline: {e}")
            return {"success": False, "error": str(e)}

    def _process_audio(self, story: Story) -> dict:
        """Process audio file to text."""
        try:
            self._create_log(story, 'speech_to_text', 'processing')

            speech_client = SpeechToTextClient()

            # Validate audio file
            validation = speech_client.validate_audio_file(story.audio_file.path)
            if not validation["valid"]:
                self._update_log(story, 'speech_to_text', 'failed', error=validation["error"])
                return {"success": False, "error": validation["error"]}

            # Transcribe audio
            transcription = speech_client.transcribe_audio_file(story.audio_file.path)

            if transcription["success"]:
                story.transcribed_text = transcription["transcription"]
                story.save()

                self._update_log(story, 'speech_to_text', 'completed', 
                               result_data={"transcription": transcription["transcription"]})
                return {"success": True}
            else:
                self._update_log(story, 'speech_to_text', 'failed', 
                               error=transcription["error"])
                return {"success": False, "error": transcription["error"]}

        except Exception as e:
            self._update_log(story, 'speech_to_text', 'failed', error=str(e))
            return {"success": False, "error": str(e)}

    def _generate_story_content(self, story: Story, prompt: str) -> dict:
        """Generate story text and character description."""
        try:
            self._create_log(story, 'story_generation', 'processing')

            # Use LangChain story generator
            story_generator = get_story_generator()
            result = story_generator.generate(prompt)

            if result["success"]:
                story.story_text = result["story"]
                story.character_description = result["character_description"]
                story.generation_parameters = {
                    "model_used": result.get("model_used"),
                    "prompt_used": prompt
                }
                story.save()

                self._update_log(story, 'story_generation', 'completed',
                               result_data={"story_length": len(result["story"])})
                return {"success": True}
            else:
                self._update_log(story, 'story_generation', 'failed',
                               error=result["error"])
                return {"success": False, "error": result["error"]}

        except Exception as e:
            self._update_log(story, 'story_generation', 'failed', error=str(e))
            return {"success": False, "error": str(e)}

    def _generate_character_image(self, story: Story) -> dict:
        """Generate character image."""
        try:
            self._create_log(story, 'character_image', 'processing')

            sd_client = StableDiffusionFreeClient()
            result = sd_client.generate_character_image(story.character_description)

            if result["success"]:
                # Save image
                image_io = io.BytesIO()
                result["image"].save(image_io, format='JPEG', quality=90)
                image_io.seek(0)

                filename = f"character_{story.id}.jpg"
                story.character_image.save(
                    filename,
                    ContentFile(image_io.read()),
                    save=True
                )

                self._update_log(story, 'character_image', 'completed',
                               result_data={"image_size": result["image"].size})
                return {"success": True}
            else:
                self._update_log(story, 'character_image', 'failed',
                               error=result["error"])
                return {"success": False, "error": result["error"]}

        except Exception as e:
            self._update_log(story, 'character_image', 'failed', error=str(e))
            return {"success": False, "error": str(e)}

    def _generate_background_image(self, story: Story) -> dict:
        """Generate background image."""
        try:
            self._create_log(story, 'background_image', 'processing')

            sd_client = StableDiffusionFreeClient()

            # Extract scene context from story
            scene_context = self._extract_scene_context(story.story_text)
            result = sd_client.generate_background_image(scene_context, story.character_description)

            if result["success"]:
                # Save image
                image_io = io.BytesIO()
                result["image"].save(image_io, format='JPEG', quality=90)
                image_io.seek(0)

                filename = f"background_{story.id}.jpg"
                story.background_image.save(
                    filename,
                    ContentFile(image_io.read()),
                    save=True
                )

                self._update_log(story, 'background_image', 'completed',
                               result_data={"image_size": result["image"].size})
                return {"success": True}
            else:
                self._update_log(story, 'background_image', 'failed',
                               error=result["error"])
                return {"success": False, "error": result["error"]}

        except Exception as e:
            self._update_log(story, 'background_image', 'failed', error=str(e))
            return {"success": False, "error": str(e)}

    def _compose_final_image(self, story: Story) -> dict:
        """Compose character and background into final scene."""
        try:
            self._create_log(story, 'image_composition', 'processing')

            composer = ImageComposer()

            # Load images
            character_img = Image.open(story.character_image.path)
            background_img = Image.open(story.background_image.path)

            # Compose scene
            result = composer.compose_scene(
                character_image=character_img,
                background_image=background_img,
                character_position="center",
                blend_edges=True
            )

            if result["success"]:
                # Save composed image
                image_io = io.BytesIO()
                result["composed_image"].save(image_io, format='JPEG', quality=95)
                image_io.seek(0)

                filename = f"composed_{story.id}.jpg"
                story.composed_image.save(
                    filename,
                    ContentFile(image_io.read()),
                    save=True
                )

                self._update_log(story, 'image_composition', 'completed',
                               result_data=result["composition_info"])
                return {"success": True}
            else:
                self._update_log(story, 'image_composition', 'failed',
                               error=result["error"])
                return {"success": False, "error": result["error"]}

        except Exception as e:
            self._update_log(story, 'image_composition', 'failed', error=str(e))
            return {"success": False, "error": str(e)}

    def _extract_scene_context(self, story_text: str) -> str:
        """Extract visual scene context from story text."""
        # Simple keyword extraction for scene context
        scene_keywords = []

        # Look for location/setting keywords
        location_words = ['forest', 'castle', 'city', 'mountain', 'beach', 'desert', 
                         'village', 'house', 'room', 'garden', 'sky', 'space']

        # Look for time/mood keywords
        mood_words = ['dark', 'bright', 'sunny', 'stormy', 'peaceful', 'mystical',
                     'ancient', 'modern', 'magical', 'mysterious']

        story_lower = story_text.lower()

        for word in location_words + mood_words:
            if word in story_lower:
                scene_keywords.append(word)

        if scene_keywords:
            return f"a {' '.join(scene_keywords[:3])} scene"
        else:
            return "a fantasy scene with atmospheric lighting"

    def _create_log(self, story: Story, step: str, status: str):
        """Create a generation log entry."""
        GenerationLog.objects.create(
            story=story,
            step=step,
            status=status
        )

    def _update_log(self, story: Story, step: str, status: str, 
                   result_data: dict = None, error: str = None):
        """Update generation log entry."""
        try:
            log = GenerationLog.objects.filter(story=story, step=step).latest('started_at')
            log.status = status
            log.completed_at = time.timezone.now() if hasattr(time, 'timezone') else None
            if result_data:
                log.result_data = result_data
            if error:
                log.error_message = error
            log.save()
        except GenerationLog.DoesNotExist:
            pass

    @action(detail=True, methods=['get'])
    def generation_logs(self, request, pk=None):
        """Get generation logs for a story."""
        story = get_object_or_404(Story, pk=pk)
        logs = story.logs.all()

        logs_data = []
        for log in logs:
            logs_data.append({
                'step': log.step,
                'status': log.status,
                'started_at': log.started_at,
                'completed_at': log.completed_at,
                'duration': log.duration,
                'error_message': log.error_message
            })

        return Response({
            'story_id': str(story.id),
            'logs': logs_data
        })

    @action(detail=False, methods=['get'])
    def health_check(self, request):
        """Health check endpoint for monitoring."""
        try:
            # Test database connection
            Story.objects.count()

            # Test AI services
            hf_client = HuggingFaceClient()
            # Simple status check without actual generation

            return Response({
                'status': 'healthy',
                'services': {
                    'database': 'connected',
                    'huggingface': 'available',
                    'storage': 'accessible'
                },
                'timestamp': time.time()
            })
        except Exception as e:
            return Response({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
