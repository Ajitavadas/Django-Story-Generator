"""
Hugging Face API client for free text and image generation services.
"""
import requests
import base64
import io
from PIL import Image
import logging
from typing import Dict, Any, Optional
import os
from django.conf import settings

logger = logging.getLogger(__name__)

class HuggingFaceClient:
    """Client for Hugging Face Inference API (Free Tier)."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('HUGGINGFACE_API_KEY')
        self.base_url = "https://api-inference.huggingface.co/models"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else None
        }
        # Remove None headers for free tier usage
        self.headers = {k: v for k, v in self.headers.items() if v is not None}

    def generate_text(self, 
                     prompt: str, 
                     model: str = "microsoft/DialoGPT-medium",
                     max_length: int = 300,
                     temperature: float = 0.8) -> Dict[str, Any]:
        """Generate text using HuggingFace models."""
        try:
            url = f"{self.base_url}/{model}"

            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": max_length,
                    "temperature": temperature,
                    "return_full_text": False,
                    "do_sample": True
                }
            }

            response = requests.post(url, json=payload, headers=self.headers)

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    return {
                        "success": True,
                        "text": generated_text,
                        "model": model
                    }
                else:
                    return {"success": False, "error": "Unexpected response format"}
            else:
                logger.error(f"HuggingFace API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "details": response.text
                }

        except Exception as e:
            logger.error(f"Error in text generation: {e}")
            return {"success": False, "error": str(e)}

    def generate_image(self, 
                      prompt: str, 
                      model: str = "runwayml/stable-diffusion-v1-5",
                      width: int = 512,
                      height: int = 512) -> Dict[str, Any]:
        """Generate image using HuggingFace Diffusion models."""
        try:
            url = f"{self.base_url}/{model}"

            payload = {
                "inputs": prompt,
                "parameters": {
                    "width": width,
                    "height": height,
                    "num_inference_steps": 20,  # Lower for faster generation
                    "guidance_scale": 7.5
                }
            }

            response = requests.post(url, json=payload, headers=self.headers)

            if response.status_code == 200:
                # Response should be image bytes
                image_bytes = response.content

                # Convert to PIL Image for processing
                image = Image.open(io.BytesIO(image_bytes))

                return {
                    "success": True,
                    "image": image,
                    "image_bytes": image_bytes,
                    "model": model
                }
            else:
                logger.error(f"Image generation error: {response.status_code}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "details": response.text
                }

        except Exception as e:
            logger.error(f"Error in image generation: {e}")
            return {"success": False, "error": str(e)}

    def check_model_status(self, model: str) -> Dict[str, Any]:
        """Check if a model is loaded and ready."""
        try:
            url = f"{self.base_url}/{model}"
            response = requests.post(url, json={"inputs": "test"}, headers=self.headers)

            if response.status_code == 503:
                # Model is loading
                return {"loaded": False, "status": "loading"}
            elif response.status_code == 200:
                return {"loaded": True, "status": "ready"}
            else:
                return {"loaded": False, "status": "error", "code": response.status_code}

        except Exception as e:
            return {"loaded": False, "status": "error", "error": str(e)}


class StableDiffusionFreeClient:
    """Free Stable Diffusion client using various free services."""

    def __init__(self):
        self.hf_client = HuggingFaceClient()

        # List of free Stable Diffusion models
        self.free_models = [
            "runwayml/stable-diffusion-v1-5",
            "CompVis/stable-diffusion-v1-4",
            "stabilityai/stable-diffusion-2-1",
        ]

    def generate_character_image(self, description: str) -> Dict[str, Any]:
        """Generate character image with optimized prompts."""
        # Enhance prompt for character generation
        enhanced_prompt = f"portrait of {description}, detailed character art, high quality, professional artwork, centered composition"

        return self._generate_with_fallback(enhanced_prompt, "character")

    def generate_background_image(self, story_context: str, character_desc: str = "") -> Dict[str, Any]:
        """Generate background image based on story context."""
        # Create background-focused prompt
        background_prompt = f"detailed background scene, {story_context}, atmospheric lighting, no characters, landscape, environment art"

        return self._generate_with_fallback(background_prompt, "background")

    def _generate_with_fallback(self, prompt: str, image_type: str) -> Dict[str, Any]:
        """Generate image with model fallback."""
        for model in self.free_models:
            try:
                logger.info(f"Attempting {image_type} generation with {model}")

                # Check model status first
                status = self.hf_client.check_model_status(model)
                if not status.get("loaded", False):
                    logger.warning(f"Model {model} not ready, trying next...")
                    continue

                result = self.hf_client.generate_image(
                    prompt=prompt,
                    model=model,
                    width=512,
                    height=512
                )

                if result["success"]:
                    result["image_type"] = image_type
                    return result
                else:
                    logger.warning(f"Failed with {model}: {result.get('error')}")

            except Exception as e:
                logger.error(f"Error with model {model}: {e}")
                continue

        # All models failed
        return {
            "success": False,
            "error": "All available models failed to generate image",
            "image_type": image_type
        }
