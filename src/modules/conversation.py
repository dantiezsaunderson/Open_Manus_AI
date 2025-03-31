"""
Conversation Module

This module handles natural language conversations with users through
the Open Manus AI system.
"""

import logging
from src.core.ai_engine import AIEngine
from src.core.memory_manager import MemoryManager

# Configure logging
logger = logging.getLogger(__name__)

class ConversationModule:
    """
    Conversation Module for handling natural language interactions with users.
    """
    
    def __init__(self, ai_engine, memory_manager):
        """
        Initialize the Conversation Module.
        
        Args:
            ai_engine (AIEngine): The AI engine instance
            memory_manager (MemoryManager): The memory manager instance
        """
        self.ai_engine = ai_engine
        self.memory_manager = memory_manager
        self.conversation_history = {}
        logger.info("Conversation Module initialized")
    
    def get_response(self, user_id, message, include_history=True):
        """
        Get a response to a user message.
        
        Args:
            user_id (str): Unique identifier for the user
            message (str): The user's message
            include_history (bool, optional): Whether to include conversation history
            
        Returns:
            str: The AI's response
        """
        try:
            # Initialize conversation history for new users
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # Build prompt with or without history
            if include_history and self.conversation_history[user_id]:
                # Get user preferences from memory if available
                user_name = self.memory_manager.get_memory(user_id, "name", "User")
                user_preferences = self.memory_manager.get_memory(user_id, "preferences", {})
                
                # Build system message with user context
                system_message = f"You are Open Manus AI, an advanced AI assistant. "
                system_message += f"You are speaking with {user_name}. "
                
                if user_preferences:
                    pref_str = ", ".join([f"{k}: {v}" for k, v in user_preferences.items()])
                    system_message += f"Their preferences include: {pref_str}. "
                
                # Add conversation history
                history = "\n".join([
                    f"{'User' if i % 2 == 0 else 'AI'}: {msg}"
                    for i, msg in enumerate(self.conversation_history[user_id][-10:])  # Last 5 exchanges (10 messages)
                ])
                
                prompt = f"Conversation history:\n{history}\n\nUser's new message: {message}\n\nYour response:"
            else:
                system_message = "You are Open Manus AI, an advanced AI assistant. Provide a helpful, friendly response."
                prompt = message
            
            # Get response from AI engine
            response = self.ai_engine.generate_response(prompt, system_message=system_message)
            
            # Update conversation history
            self.conversation_history[user_id].append(message)
            self.conversation_history[user_id].append(response)
            
            # Limit history size
            if len(self.conversation_history[user_id]) > 100:  # Keep last 50 exchanges
                self.conversation_history[user_id] = self.conversation_history[user_id][-100:]
            
            return response
            
        except Exception as e:
            logger.error(f"Error in conversation: {e}")
            return "I apologize, but I encountered an error processing your message. Please try again."
    
    def clear_history(self, user_id):
        """
        Clear conversation history for a user.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            bool: Success status
        """
        try:
            if user_id in self.conversation_history:
                self.conversation_history[user_id] = []
            return True
        except Exception as e:
            logger.error(f"Error clearing conversation history: {e}")
            return False
    
    def extract_preferences(self, user_id, message):
        """
        Extract user preferences from a message and store them in memory.
        
        Args:
            user_id (str): Unique identifier for the user
            message (str): The user's message
            
        Returns:
            dict: Extracted preferences
        """
        try:
            # Use AI to extract preferences
            system_message = "You are a preference extraction system. Extract any user preferences from the message and return them as a JSON object with preference categories as keys and values. Only extract clear preferences, not assumptions."
            
            response = self.ai_engine.generate_response(message, system_message=system_message)
            
            # Try to parse response as JSON
            import json
            try:
                preferences = json.loads(response)
                
                # Store preferences in memory
                current_prefs = self.memory_manager.get_memory(user_id, "preferences", {})
                current_prefs.update(preferences)
                self.memory_manager.save_memory(user_id, "preferences", current_prefs)
                
                return preferences
            except json.JSONDecodeError:
                logger.warning(f"Could not parse preferences from AI response: {response}")
                return {}
                
        except Exception as e:
            logger.error(f"Error extracting preferences: {e}")
            return {}
