"""
Image composition utilities using PIL for combining character and background images.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import io
import logging
from typing import Tuple, Optional, Dict, Any
import numpy as np

logger = logging.getLogger(__name__)

class ImageComposer:
    """Utility class for composing character and background images."""

    def __init__(self):
        self.default_size = (1024, 768)  # Wider aspect ratio for scenes

    def compose_scene(self, 
                     character_image: Image.Image,
                     background_image: Image.Image,
                     character_position: str = "center",
                     blend_edges: bool = True) -> Dict[str, Any]:
        """Compose character and background into a unified scene."""
        try:
            # Resize images to work with
            bg_resized = self._resize_image(background_image, self.default_size)

            # Calculate character size (should be smaller than background)
            char_width = int(self.default_size[0] * 0.4)  # 40% of background width
            char_height = int(char_width * 1.2)  # Slightly taller ratio

            char_resized = self._resize_image(character_image, (char_width, char_height))

            # Create composition
            composed = self._blend_images(bg_resized, char_resized, character_position, blend_edges)

            return {
                "success": True,
                "composed_image": composed,
                "dimensions": composed.size,
                "composition_info": {
                    "character_position": character_position,
                    "character_size": char_resized.size,
                    "background_size": bg_resized.size,
                    "blend_edges": blend_edges
                }
            }

        except Exception as e:
            logger.error(f"Error composing scene: {e}")
            return {"success": False, "error": str(e)}

    def _resize_image(self, image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Resize image while maintaining aspect ratio."""
        # Calculate aspect ratio
        img_ratio = image.width / image.height
        target_ratio = target_size[0] / target_size[1]

        if img_ratio > target_ratio:
            # Image is wider than target
            new_height = target_size[1]
            new_width = int(new_height * img_ratio)
        else:
            # Image is taller than target
            new_width = target_size[0]
            new_height = int(new_width / img_ratio)

        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Crop to exact target size if needed
        if resized.size != target_size:
            left = (resized.width - target_size[0]) // 2
            top = (resized.height - target_size[1]) // 2
            right = left + target_size[0]
            bottom = top + target_size[1]
            resized = resized.crop((left, top, right, bottom))

        return resized

    def _blend_images(self, 
                     background: Image.Image, 
                     character: Image.Image, 
                     position: str,
                     blend_edges: bool) -> Image.Image:
        """Blend character onto background."""
        # Create a copy of background to work with
        composed = background.copy()

        # Calculate position for character
        char_x, char_y = self._calculate_position(
            background.size, character.size, position
        )

        if blend_edges:
            # Create soft mask for better blending
            mask = self._create_soft_mask(character.size)
            character_with_alpha = character.copy()
            character_with_alpha.putalpha(mask)
            composed.paste(character_with_alpha, (char_x, char_y), character_with_alpha)
        else:
            # Simple paste
            if character.mode == 'RGBA':
                composed.paste(character, (char_x, char_y), character)
            else:
                composed.paste(character, (char_x, char_y))

        return composed

    def _calculate_position(self, 
                          bg_size: Tuple[int, int], 
                          char_size: Tuple[int, int], 
                          position: str) -> Tuple[int, int]:
        """Calculate character position on background."""
        bg_w, bg_h = bg_size
        char_w, char_h = char_size

        positions = {
            "center": ((bg_w - char_w) // 2, (bg_h - char_h) // 2),
            "left": (bg_w // 6, (bg_h - char_h) // 2),
            "right": (bg_w - char_w - bg_w // 6, (bg_h - char_h) // 2),
            "bottom_center": ((bg_w - char_w) // 2, bg_h - char_h - 50),
            "top_center": ((bg_w - char_w) // 2, 50)
        }

        return positions.get(position, positions["center"])

    def _create_soft_mask(self, size: Tuple[int, int], fade_distance: int = 20) -> Image.Image:
        """Create a soft-edged mask for better blending."""
        mask = Image.new('L', size, 255)

        # Create fade effect at edges
        draw = ImageDraw.Draw(mask)
        width, height = size

        # Draw gradient rectangles for soft edges
        for i in range(fade_distance):
            alpha = int(255 * (i / fade_distance))
            draw.rectangle(
                [(i, i), (width - i - 1, height - i - 1)],
                outline=alpha,
                width=1
            )

        # Apply Gaussian blur for smoother transition
        mask = mask.filter(ImageFilter.GaussianBlur(radius=2))

        return mask

    def create_collage(self, images: list, layout: str = "grid") -> Dict[str, Any]:
        """Create a collage of multiple images."""
        try:
            if not images:
                return {"success": False, "error": "No images provided"}

            if layout == "grid":
                return self._create_grid_collage(images)
            elif layout == "horizontal":
                return self._create_horizontal_collage(images)
            else:
                return {"success": False, "error": f"Unsupported layout: {layout}"}

        except Exception as e:
            logger.error(f"Error creating collage: {e}")
            return {"success": False, "error": str(e)}

    def _create_grid_collage(self, images: list) -> Dict[str, Any]:
        """Create a grid-based collage."""
        num_images = len(images)

        # Determine grid dimensions
        if num_images <= 4:
            cols = 2
            rows = (num_images + 1) // 2
        else:
            cols = 3
            rows = (num_images + 2) // 3

        # Resize all images to same size
        thumb_size = (300, 300)
        thumbnails = []
        for img in images:
            thumb = self._resize_image(img, thumb_size)
            thumbnails.append(thumb)

        # Create collage canvas
        canvas_width = cols * thumb_size[0]
        canvas_height = rows * thumb_size[1]
        collage = Image.new('RGB', (canvas_width, canvas_height), 'white')

        # Paste images
        for i, thumb in enumerate(thumbnails):
            row = i // cols
            col = i % cols
            x = col * thumb_size[0]
            y = row * thumb_size[1]
            collage.paste(thumb, (x, y))

        return {
            "success": True,
            "collage": collage,
            "layout": "grid",
            "dimensions": collage.size
        }

    def enhance_image(self, image: Image.Image, enhancement_type: str = "auto") -> Image.Image:
        """Apply enhancements to improve image quality."""
        enhanced = image.copy()

        if enhancement_type == "auto" or enhancement_type == "contrast":
            enhancer = ImageEnhance.Contrast(enhanced)
            enhanced = enhancer.enhance(1.2)  # Increase contrast by 20%

        if enhancement_type == "auto" or enhancement_type == "color":
            enhancer = ImageEnhance.Color(enhanced)
            enhanced = enhancer.enhance(1.1)  # Increase color saturation by 10%

        if enhancement_type == "auto" or enhancement_type == "sharpness":
            enhancer = ImageEnhance.Sharpness(enhanced)
            enhanced = enhancer.enhance(1.1)  # Increase sharpness by 10%

        return enhanced

    def save_image(self, image: Image.Image, filepath: str, quality: int = 95) -> bool:
        """Save image with optimization."""
        try:
            # Ensure RGB mode for JPEG
            if image.mode in ('RGBA', 'P'):
                if filepath.lower().endswith(('.jpg', '.jpeg')):
                    # Create white background for JPEG
                    bg = Image.new('RGB', image.size, 'white')
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    bg.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = bg

            image.save(filepath, quality=quality, optimize=True)
            return True
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return False
