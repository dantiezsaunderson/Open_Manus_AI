"""
AI Engine Module

This module serves as the core AI engine for Open Manus AI, handling interactions with
the OpenAI GPT-4 API and providing the foundation for all AI capabilities.
"""

import os
import logging
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class AIEngine:
    """
    Core AI Engine class that handles interactions with the OpenAI API.
    """
    
    def __init__(self):
        """Initialize the AI Engine with API credentials."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            logger.warning("OpenAI API key not found in environment variables")
        else:
            openai.api_key = self.api_key
            logger.info("AI Engine initialized successfully")
    
    def generate_response(self, prompt, system_message=None, temperature=0.7, max_tokens=1000):
        """
        Generate a response using the OpenAI GPT-4 API.
        
        Args:
            prompt (str): The user prompt to generate a response for
            system_message (str, optional): System message to guide the AI's behavior
            temperature (float, optional): Controls randomness in the response
            max_tokens (int, optional): Maximum number of tokens in the response
            
        Returns:
            str: The generated response text
        """
        try:
            messages = []
            
            # Add system message if provided
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            # Add user prompt
            messages.append({"role": "user", "content": prompt})
            
            # Call the OpenAI API
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def analyze_code(self, code, language):
        """
        Analyze code using the AI model.
        
        Args:
            code (str): The code to analyze
            language (str): The programming language of the code
            
        Returns:
            dict: Analysis results including suggestions and potential issues
        """
        system_message = f"You are a code analysis expert. Analyze the following {language} code and provide suggestions for improvement, identify potential bugs, and assess code quality."
        
        try:
            response = self.generate_response(code, system_message=system_message)
            return {
                "analysis": response,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return {
                "analysis": f"Error analyzing code: {str(e)}",
                "success": False
            }
    
    def analyze_financial_data(self, data):
        """
        Analyze financial data using the AI model.
        
        Args:
            data (str): Financial data to analyze
            
        Returns:
            dict: Analysis results including insights and recommendations
        """
        system_message = "You are a financial analysis expert. Analyze the provided financial data and provide insights, trends, and recommendations."
        
        try:
            response = self.generate_response(data, system_message=system_message)
            return {
                "analysis": response,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error analyzing financial data: {e}")
            return {
                "analysis": f"Error analyzing financial data: {str(e)}",
                "success": False
            }
