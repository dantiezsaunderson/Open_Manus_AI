"""
Enhanced Conversation Module

This module provides improved conversation capabilities for the Open Manus AI system,
leveraging the enhanced memory system for more personalized and context-aware interactions.
"""

import logging
import json
import os
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import re

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedConversationModule:
    """
    Enhanced Conversation Module for more personalized and context-aware interactions.
    
    This class provides improved conversation capabilities with:
    - Context-aware responses using the enhanced memory system
    - Conversation flow management with topic tracking
    - Personalized responses based on user preferences
    - Multi-turn conversation handling
    - Conversation summarization and continuation
    """
    
    def __init__(self, ai_engine=None, memory_manager=None):
        """
        Initialize the Enhanced Conversation Module.
        
        Args:
            ai_engine (AIEngine, optional): AI engine for generating responses
            memory_manager (EnhancedMemoryManager, optional): Memory manager for context and personalization
        """
        self.ai_engine = ai_engine
        self.memory_manager = memory_manager
        self.active_conversations = {}
        self.conversation_contexts = {}
        logger.info("Enhanced Conversation Module initialized")
    
    def start_conversation(self, user_id: str, initial_message: str = None) -> Dict[str, Any]:
        """
        Start a new conversation.
        
        Args:
            user_id (str): User ID
            initial_message (str, optional): Initial user message
            
        Returns:
            dict: Conversation information
        """
        try:
            # Create a new conversation in memory manager
            if not self.memory_manager:
                conversation_id = str(uuid.uuid4())
            else:
                conversation_id = self.memory_manager.create_conversation(user_id)
            
            # Initialize conversation context
            self.conversation_contexts[conversation_id] = {
                "user_id": user_id,
                "start_time": datetime.now().isoformat(),
                "last_update_time": datetime.now().isoformat(),
                "topics": [],
                "entities": {},
                "sentiment": "neutral",
                "message_count": 0
            }
            
            # Add to active conversations
            self.active_conversations[conversation_id] = {
                "user_id": user_id,
                "start_time": datetime.now().isoformat(),
                "last_update_time": datetime.now().isoformat(),
                "message_count": 0
            }
            
            # Process initial message if provided
            response = None
            if initial_message:
                response = self.process_message(conversation_id, initial_message)
            
            return {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "start_time": self.conversation_contexts[conversation_id]["start_time"],
                "initial_response": response
            }
            
        except Exception as e:
            logger.error(f"Error starting conversation for user {user_id}: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def process_message(self, conversation_id: str, message: str) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            conversation_id (str): Conversation ID
            message (str): User message
            
        Returns:
            dict: Response information
        """
        try:
            # Check if conversation exists
            if conversation_id not in self.conversation_contexts:
                return {
                    "error": "Conversation not found",
                    "success": False
                }
            
            context = self.conversation_contexts[conversation_id]
            user_id = context["user_id"]
            
            # Update conversation context
            context["last_update_time"] = datetime.now().isoformat()
            context["message_count"] += 1
            
            # Update active conversations
            if conversation_id in self.active_conversations:
                self.active_conversations[conversation_id]["last_update_time"] = datetime.now().isoformat()
                self.active_conversations[conversation_id]["message_count"] += 1
            
            # Store message in memory manager
            if self.memory_manager:
                self.memory_manager.add_message(conversation_id, user_id, "user", message)
            
            # Analyze message for context updates
            self._analyze_message(conversation_id, message)
            
            # Get conversation context from memory manager
            memory_context = {}
            if self.memory_manager:
                memory_context = self.memory_manager.get_context(user_id, conversation_id)
            
            # Generate response
            response_text = self._generate_response(conversation_id, message, memory_context)
            
            # Store response in memory manager
            if self.memory_manager and response_text:
                self.memory_manager.add_message(conversation_id, user_id, "assistant", response_text)
            
            # Update conversation summary periodically
            if self.memory_manager and context["message_count"] % 10 == 0:
                self.memory_manager.summarize_conversation(conversation_id, self.ai_engine)
            
            return {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "response": response_text,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error processing message for conversation {conversation_id}: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def _analyze_message(self, conversation_id: str, message: str):
        """
        Analyze a user message to update conversation context.
        
        Args:
            conversation_id (str): Conversation ID
            message (str): User message
        """
        context = self.conversation_contexts[conversation_id]
        
        # Extract potential topics
        # This is a simple implementation; a more sophisticated approach would use NLP
        words = re.findall(r'\b\w+\b', message.lower())
        potential_topics = [word for word in words if len(word) > 3 and word not in self._get_stopwords()]
        
        # Update topics
        for topic in potential_topics[:3]:  # Limit to top 3 potential topics
            if topic not in context["topics"]:
                context["topics"].append(topic)
        
        # Limit topics list to most recent 10
        context["topics"] = context["topics"][-10:]
        
        # Simple sentiment analysis
        # This is a very basic implementation; a real system would use a proper sentiment analyzer
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "happy", "pleased", "love", "like", "thanks"]
        negative_words = ["bad", "terrible", "awful", "horrible", "sad", "angry", "upset", "hate", "dislike", "sorry"]
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            context["sentiment"] = "positive"
        elif negative_count > positive_count:
            context["sentiment"] = "negative"
        else:
            context["sentiment"] = "neutral"
        
        # Extract entities (very simple implementation)
        # A real system would use named entity recognition
        entities = re.findall(r'(?<!\w)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', message)
        for entity in entities:
            if entity not in context["entities"]:
                context["entities"][entity] = 1
            else:
                context["entities"][entity] += 1
    
    def _get_stopwords(self):
        """
        Get a list of stopwords to filter out from topic extraction.
        
        Returns:
            list: List of stopwords
        """
        # Simple list of common English stopwords
        return [
            "the", "and", "that", "have", "for", "not", "with", "you", "this", "but",
            "his", "from", "they", "she", "will", "would", "there", "their", "what",
            "about", "which", "when", "make", "like", "time", "just", "know", "take",
            "into", "year", "your", "good", "some", "could", "them", "than", "then",
            "look", "only", "come", "over", "think", "also", "back", "after", "work",
            "first", "well", "even", "want", "because", "these", "give", "most"
        ]
    
    def _generate_response(self, conversation_id: str, message: str, memory_context: Dict[str, Any]) -> str:
        """
        Generate a response to a user message.
        
        Args:
            conversation_id (str): Conversation ID
            message (str): User message
            memory_context (dict): Context from memory manager
            
        Returns:
            str: Generated response
        """
        if not self.ai_engine:
            return "AI engine not available. Please configure the AI engine to enable conversation."
        
        # Get conversation context
        context = self.conversation_contexts[conversation_id]
        
        # Prepare system message with context
        system_message = self._create_system_message(context, memory_context)
        
        # Get recent conversation history
        conversation_history = []
        if self.memory_manager:
            recent_messages = memory_context.get("recent_messages", [])
            for msg in recent_messages:
                conversation_history.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Generate response
        response = self.ai_engine.generate_response(
            message, 
            system_message=system_message,
            conversation_history=conversation_history
        )
        
        return response
    
    def _create_system_message(self, context: Dict[str, Any], memory_context: Dict[str, Any]) -> str:
        """
        Create a system message with context for the AI.
        
        Args:
            context (dict): Conversation context
            memory_context (dict): Context from memory manager
            
        Returns:
            str: System message
        """
        # Start with base system message
        system_message = "You are Open Manus AI, a helpful and personalized assistant. "
        
        # Add user information if available
        user_info = memory_context.get("user", {})
        if user_info and user_info.get("name"):
            system_message += f"You are speaking with {user_info['name']}. "
        
        # Add user preferences if available
        preferences = memory_context.get("preferences", {})
        if preferences:
            system_message += "User preferences: "
            
            # Add communication preferences
            if "communication" in preferences:
                comm_prefs = preferences["communication"]
                if "style" in comm_prefs:
                    system_message += f"Preferred communication style: {comm_prefs['style']}. "
                if "detail_level" in comm_prefs:
                    system_message += f"Preferred detail level: {comm_prefs['detail_level']}. "
            
            # Add topic preferences
            if "topics" in preferences:
                topic_prefs = preferences["topics"]
                interests = topic_prefs.get("interests", [])
                if interests:
                    system_message += f"Interested in: {', '.join(interests)}. "
                
                dislikes = topic_prefs.get("dislikes", [])
                if dislikes:
                    system_message += f"Dislikes: {', '.join(dislikes)}. "
        
        # Add relevant facts if available
        relevant_facts = memory_context.get("relevant_facts", [])
        if relevant_facts:
            system_message += "Relevant information about the user: "
            for fact in relevant_facts[:3]:  # Limit to top 3 facts
                system_message += f"{fact['content']}. "
        
        # Add conversation context
        system_message += "Current conversation context: "
        
        # Add topics
        if context.get("topics"):
            system_message += f"Topics discussed: {', '.join(context['topics'][:5])}. "
        
        # Add sentiment
        system_message += f"Current sentiment: {context.get('sentiment', 'neutral')}. "
        
        # Add entities
        if context.get("entities"):
            top_entities = sorted(context["entities"].items(), key=lambda x: x[1], reverse=True)[:3]
            if top_entities:
                system_message += f"Key entities mentioned: {', '.join(entity for entity, count in top_entities)}. "
        
        # Add instructions for response
        system_message += "Please provide a helpful, personalized response that takes this context into account. "
        system_message += "Be conversational and engaging while providing accurate and relevant information."
        
        return system_message
    
    def end_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        End a conversation and generate a summary.
        
        Args:
            conversation_id (str): Conversation ID
            
        Returns:
            dict: Conversation summary
        """
        try:
            # Check if conversation exists
            if conversation_id not in self.conversation_contexts:
                return {
                    "error": "Conversation not found",
                    "success": False
                }
            
            context = self.conversation_contexts[conversation_id]
            user_id = context["user_id"]
            
            # Generate summary
            summary = ""
            if self.memory_manager:
                summary = self.memory_manager.summarize_conversation(conversation_id, self.ai_engine)
            
            # Remove from active conversations
            if conversation_id in self.active_conversations:
                del self.active_conversations[conversation_id]
            
            # Keep context for potential future reference
            # In a production system, you might want to clean this up periodically
            
            return {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "start_time": context["start_time"],
                "end_time": datetime.now().isoformat(),
                "message_count": context["message_count"],
                "topics": context["topics"],
                "summary": summary,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error ending conversation {conversation_id}: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def get_active_conversations(self, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Get a list of active conversations.
        
        Args:
            user_id (str, optional): Filter by user ID
            
        Returns:
            list: List of active conversations
        """
        active_convs = []
        
        for conv_id, conv_data in self.active_conversations.items():
            if user_id is None or conv_data["user_id"] == user_id:
                active_convs.append({
                    "conversation_id": conv_id,
                    "user_id": conv_data["user_id"],
                    "start_time": conv_data["start_time"],
                    "last_update_time": conv_data["last_update_time"],
                    "message_count": conv_data["message_count"]
                })
        
        return active_convs
    
    def get_conversation_context(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get the context for a conversation.
        
        Args:
            conversation_id (str): Conversation ID
            
        Returns:
            dict: Conversation context
        """
        if conversation_id not in self.conversation_contexts:
            return {
                "error": "Conversation not found",
                "success": False
            }
        
        return {
            "conversation_id": conversation_id,
            "context": self.conversation_contexts[conversation_id],
            "success": True
        }
    
    def continue_conversation(self, user_id: str, previous_conversation_id: str, message: str) -> Dict[str, Any]:
        """
        Continue a previous conversation with a new conversation ID.
        
        Args:
            user_id (str): User ID
            previous_conversation_id (str): Previous conversation ID
            message (str): Initial message for the new conversation
            
        Returns:
            dict: New conversation information
        """
        try:
            # Check if previous conversation exists
            if previous_conversation_id not in self.conversation_contexts:
                return {
                    "error": "Previous conversation not found",
                    "success": False
                }
            
            # Get previous context
            previous_context = self.conversation_contexts[previous_conversation_id]
            
            # Start a new conversation
            new_conversation = self.start_conversation(user_id)
            new_conversation_id = new_conversation["conversation_id"]
            
            # Copy relevant context
            self.conversation_contexts[new_conversation_id]["topics"] = previous_context["topics"].copy()
            self.conversation_contexts[new_conversation_id]["entities"] = previous_context["entities"].copy()
            
            # Add a reference to the previous conversation
            self.conversation_contexts[new_conversation_id]["previous_conversation_id"] = previous_conversation_id
            
            # Process initial message
            response = self.process_message(new_conversation_id, message)
            
            return {
                "conversation_id": new_conversation_id,
                "user_id": user_id,
                "start_time": self.conversation_contexts[new_conversation_id]["start_time"],
                "previous_conversation_id": previous_conversation_id,
                "initial_response": response,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error continuing conversation {previous_conversation_id} for user {user_id}: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def set_conversation_preference(self, user_id: str, category: str, key: str, value: Any) -> bool:
        """
        Set a conversation preference for a user.
        
        Args:
            user_id (str): User ID
            category (str): Preference category
            key (str): Preference key
            value (Any): Preference value
            
        Returns:
            bool: Success status
        """
        if not self.memory_manager:
            return False
        
        return self.memory_manager.set_preference(user_id, category, key, value)
    
    def get_conversation_preference(self, user_id: str, category: str, key: str, default: Any = None) -> Any:
        """
        Get a conversation preference for a user.
        
        Args:
            user_id (str): User ID
            category (str): Preference category
            key (str): Preference key
            default (Any, optional): Default value if preference not found
            
        Returns:
            Any: Preference value
        """
        if not self.memory_manager:
            return default
        
        return self.memory_manager.get_preference(user_id, category, key, default)
    
    def analyze_conversation_patterns(self, user_id: str) -> Dict[str, Any]:
        """
        Analyze conversation patterns for a user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: Analysis results
        """
        try:
            if not self.memory_manager:
                return {
                    "error": "Memory manager not available",
                    "success": False
                }
            
            # Get all conversations for the user
            conversations = self.memory_manager.get_user_conversations(user_id, limit=100)
            
            if not conversations:
                return {
                    "user_id": user_id,
                    "message": "No conversations found for analysis",
                    "success": True
                }
            
            # Analyze patterns
            total_messages = 0
            topics_frequency = {}
            sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
            
            for conv_id in [conv["conversation_id"] for conv in conversations]:
                if conv_id in self.conversation_contexts:
                    context = self.conversation_contexts[conv_id]
                    
                    # Count messages
                    total_messages += context.get("message_count", 0)
                    
                    # Count topics
                    for topic in context.get("topics", []):
                        if topic not in topics_frequency:
                            topics_frequency[topic] = 0
                        topics_frequency[topic] += 1
                    
                    # Count sentiment
                    sentiment = context.get("sentiment", "neutral")
                    sentiment_counts[sentiment] += 1
            
            # Get top topics
            top_topics = sorted(topics_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Calculate sentiment distribution
            total_convs = len(conversations)
            sentiment_distribution = {
                "positive": sentiment_counts["positive"] / total_convs if total_convs > 0 else 0,
                "neutral": sentiment_counts["neutral"] / total_convs if total_convs > 0 else 0,
                "negative": sentiment_counts["negative"] / total_convs if total_convs > 0 else 0
            }
            
            return {
                "user_id": user_id,
                "total_conversations": total_convs,
                "total_messages": total_messages,
                "avg_messages_per_conversation": total_messages / total_convs if total_convs > 0 else 0,
                "top_topics": top_topics,
                "sentiment_distribution": sentiment_distribution,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error analyzing conversation patterns for user {user_id}: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def get_conversation_suggestions(self, user_id: str) -> List[str]:
        """
        Get conversation topic suggestions for a user based on their history.
        
        Args:
            user_id (str): User ID
            
        Returns:
            list: List of suggested topics
        """
        try:
            if not self.memory_manager:
                return []
            
            # Get user preferences
            preferences = self.memory_manager.get_all_preferences(user_id)
            interests = preferences.get("topics", {}).get("interests", [])
            
            # Get facts about the user
            facts = self.memory_manager.get_facts(user_id, category="personal", limit=10)
            
            # Get conversation analysis
            analysis = self.analyze_conversation_patterns(user_id)
            top_topics = [topic for topic, _ in analysis.get("top_topics", [])]
            
            # Combine sources for suggestions
            suggestions = []
            
            # Add suggestions based on interests
            for interest in interests:
                suggestions.append(f"Tell me more about {interest}")
            
            # Add suggestions based on facts
            for fact in facts:
                content = fact.get("content", "")
                if "like" in content.lower() or "interest" in content.lower():
                    suggestions.append(f"Can you recommend something related to {content}")
            
            # Add suggestions based on top topics
            for topic in top_topics:
                suggestions.append(f"Let's talk more about {topic}")
            
            # Add some generic suggestions
            generic_suggestions = [
                "What's new in technology today?",
                "Can you help me learn something new?",
                "I'd like some financial advice",
                "Tell me an interesting fact",
                "How can you help me be more productive?"
            ]
            
            suggestions.extend(generic_suggestions)
            
            # Deduplicate and limit
            unique_suggestions = list(set(suggestions))
            return unique_suggestions[:10]
            
        except Exception as e:
            logger.error(f"Error getting conversation suggestions for user {user_id}: {e}")
            return []
