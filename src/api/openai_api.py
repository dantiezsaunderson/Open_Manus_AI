"""
OpenAI API Integration Module

This module provides integration with the OpenAI API for the Open Manus AI system.
"""

import os
import logging
import openai
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class OpenAIAPI:
    """
    OpenAI API integration for accessing GPT models and other OpenAI services.
    """
    
    def __init__(self):
        """Initialize the OpenAI API integration."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            logger.warning("OpenAI API key not found in environment variables")
        else:
            openai.api_key = self.api_key
            logger.info("OpenAI API integration initialized successfully")
    
    def chat_completion(self, messages, model="gpt-4", temperature=0.7, max_tokens=1000):
        """
        Generate a chat completion using the OpenAI API.
        
        Args:
            messages (list): List of message dictionaries with 'role' and 'content'
            model (str, optional): Model to use for completion
            temperature (float, optional): Controls randomness in the response
            max_tokens (int, optional): Maximum number of tokens in the response
            
        Returns:
            dict: The API response
        """
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "text": response.choices[0].message.content,
                "usage": response.usage.to_dict(),
                "model": response.model,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in OpenAI chat completion: {e}")
            return {
                "text": f"Error: {str(e)}",
                "success": False
            }
    
    def generate_image(self, prompt, size="1024x1024", quality="standard", n=1):
        """
        Generate an image using DALL-E.
        
        Args:
            prompt (str): Text description of the desired image
            size (str, optional): Image size (256x256, 512x512, or 1024x1024)
            quality (str, optional): Image quality (standard or hd)
            n (int, optional): Number of images to generate
            
        Returns:
            dict: The API response with image URLs
        """
        try:
            response = openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=n
            )
            
            return {
                "images": [item.url for item in response.data],
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in OpenAI image generation: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def transcribe_audio(self, audio_file_path, language=None):
        """
        Transcribe audio to text using Whisper.
        
        Args:
            audio_file_path (str): Path to the audio file
            language (str, optional): Language code for transcription
            
        Returns:
            dict: The API response with transcribed text
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                if language:
                    response = openai.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language
                    )
                else:
                    response = openai.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
            
            return {
                "text": response.text,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in OpenAI audio transcription: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def embed_text(self, text, model="text-embedding-ada-002"):
        """
        Generate embeddings for text using OpenAI's embedding models.
        
        Args:
            text (str): Text to embed
            model (str, optional): Embedding model to use
            
        Returns:
            dict: The API response with embeddings
        """
        try:
            response = openai.embeddings.create(
                model=model,
                input=text
            )
            
            return {
                "embedding": response.data[0].embedding,
                "usage": response.usage.to_dict(),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in OpenAI text embedding: {e}")
            return {
                "error": str(e),
                "success": False
            }
