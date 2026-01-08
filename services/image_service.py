"""
Image Service - Handles image storage and retrieval
"""
import os
from PIL import Image
from typing import Optional
from config import IMAGE_STORAGE_DIR


class ImageService:
    
    @staticmethod
    def save_image(image: Image.Image, chat_id: str) -> str:
        os.makedirs(IMAGE_STORAGE_DIR, exist_ok=True)
        image_path = os.path.join(IMAGE_STORAGE_DIR, f"{chat_id}.png")
        image.save(image_path)
        return image_path
    
    @staticmethod
    def load_image(image_path: str) -> Optional[Image.Image]:
        if os.path.exists(image_path):
            try:
                return Image.open(image_path)
            except (IOError, OSError):
                return None
        return None
