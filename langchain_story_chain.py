"""
LangChain chain for story generation using free AI services.
"""
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import BaseOutputParser
from langchain_huggingface import HuggingFacePipeline
from langchain_community.llms import HuggingFaceEndpoint
import logging
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)

class StoryOutputParser(BaseOutputParser):
    """Parser for story generation output."""

    def parse(self, text: str) -> Dict[str, str]:
        """Parse the output into story and character description."""
        try:
            # Look for section markers
            if "CHARACTER:" in text and "STORY:" in text:
                parts = text.split("CHARACTER:")
                story_part = parts[0].replace("STORY:", "").strip()
                character_part = parts[1].strip()

                return {
                    "story": story_part,
                    "character_description": character_part
                }
            else:
                # Fallback: treat as story only
                return {
                    "story": text.strip(),
                    "character_description": "A mysterious character in this tale."
                }
        except Exception as e:
            logger.error(f"Error parsing story output: {e}")
            return {
                "story": text.strip() if text else "Unable to generate story.",
                "character_description": "Unable to generate character description."
            }


class StoryGenerationChain:
    """LangChain chain for generating stories and character descriptions."""

    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        self.model_name = model_name
        self.llm = None
        self.chain = None
        self.output_parser = StoryOutputParser()
        self._initialize_chain()

    def _initialize_chain(self):
        """Initialize the LangChain components."""
        try:
            # Use HuggingFace Endpoint for free inference
            self.llm = HuggingFaceEndpoint(
                repo_id="microsoft/DialoGPT-medium",
                max_length=512,
                temperature=0.8,
                huggingfacehub_api_token=None  # Will use free tier
            )

            # Create the prompt template
            prompt_template = PromptTemplate(
                input_variables=["user_prompt"],
                template=self._get_story_template()
            )

            # Create the chain
            self.chain = LLMChain(
                llm=self.llm,
                prompt=prompt_template,
                output_parser=self.output_parser,
                verbose=True
            )

            logger.info(f"Story generation chain initialized with model: {self.model_name}")

        except Exception as e:
            logger.error(f"Failed to initialize story generation chain: {e}")
            raise

    def _get_story_template(self) -> str:
        """Get the prompt template for story generation."""
        return """You are a creative storyteller. Based on the user's prompt, create an engaging short story (200-300 words) and describe the main character (100-150 words).

User Prompt: {user_prompt}

Please format your response as follows:

STORY:
[Write an engaging short story here based on the user prompt. Make it vivid, creative, and approximately 200-300 words.]

CHARACTER:
[Provide a detailed description of the main character, including their appearance, personality, and role in the story. Make it approximately 100-150 words and suitable for image generation.]

Make sure both the story and character description are creative, vivid, and engaging. The character description should include specific visual details that would help in creating an image."""

    def generate(self, user_prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate story and character description."""
        try:
            logger.info(f"Generating story for prompt: {user_prompt[:50]}...")

            # Run the chain
            result = self.chain.run(user_prompt=user_prompt)

            # Parse the result
            parsed_result = self.output_parser.parse(result)

            logger.info("Story generation completed successfully")
            return {
                "success": True,
                "story": parsed_result["story"],
                "character_description": parsed_result["character_description"],
                "raw_output": result,
                "model_used": self.model_name
            }

        except Exception as e:
            logger.error(f"Error in story generation: {e}")
            return {
                "success": False,
                "error": str(e),
                "story": "Unable to generate story at this time. Please try again.",
                "character_description": "Unable to generate character description."
            }

    def refine_prompt(self, original_prompt: str, feedback: str) -> str:
        """Refine the prompt based on user feedback."""
        refined_prompt = f"{original_prompt}\n\nAdditional guidance: {feedback}"
        return refined_prompt


# Alternative implementation using HuggingFace Transformers directly
class LocalStoryGenerator:
    """Local story generation using HuggingFace transformers."""

    def __init__(self):
        try:
            from transformers import pipeline
            self.generator = pipeline(
                "text-generation",
                model="gpt2",
                max_length=300,
                num_return_sequences=1,
                temperature=0.8,
                do_sample=True
            )
            logger.info("Local story generator initialized")
        except ImportError:
            logger.warning("Transformers not available, falling back to remote API")
            self.generator = None

    def generate(self, prompt: str) -> Dict[str, Any]:
        """Generate story using local model."""
        if not self.generator:
            return {"success": False, "error": "Local generator not available"}

        try:
            story_prompt = f"Write a creative short story: {prompt}\n\nStory:"
            result = self.generator(story_prompt, max_length=300, truncation=True)

            story_text = result[0]['generated_text']
            # Remove the prompt part
            story_text = story_text.replace(story_prompt, "").strip()

            return {
                "success": True,
                "story": story_text,
                "character_description": "A character from this imaginative tale.",
                "model_used": "gpt2-local"
            }
        except Exception as e:
            logger.error(f"Local generation error: {e}")
            return {"success": False, "error": str(e)}


# Factory function
def get_story_generator(use_local: bool = False) -> StoryGenerationChain:
    """Get the appropriate story generator."""
    if use_local:
        return LocalStoryGenerator()
    else:
        return StoryGenerationChain()
