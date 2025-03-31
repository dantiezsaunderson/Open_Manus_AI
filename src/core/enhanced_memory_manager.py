"""
Enhanced Memory Manager Module

This module provides improved user memory and personalization features for the Open Manus AI system,
with enhanced security, persistence, and context management capabilities.
"""

import logging
import json
import os
import time
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import sqlite3
import threading

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedMemoryManager:
    """
    Enhanced Memory Manager for secure user memory and personalization features.
    
    This class provides improved memory management with:
    - Secure storage of user preferences and history
    - Long-term and short-term memory management
    - Context-aware memory retrieval
    - Memory summarization and prioritization
    - Multi-user support with isolation
    """
    
    def __init__(self, storage_dir: str = None, encryption_key: str = None):
        """
        Initialize the Enhanced Memory Manager.
        
        Args:
            storage_dir (str, optional): Directory for storing memory data
            encryption_key (str, optional): Key for encrypting sensitive data
        """
        # Set up storage directory
        self.storage_dir = storage_dir or os.path.join(os.path.expanduser("~"), ".open_manus_ai", "memory")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Set up encryption
        self.encryption_key = encryption_key or os.environ.get("MEMORY_ENCRYPTION_KEY", "default_key")
        
        # Initialize memory database
        self.db_path = os.path.join(self.storage_dir, "memory.db")
        self.init_database()
        
        # Initialize memory cache
        self.memory_cache = {}
        self.cache_lock = threading.Lock()
        
        logger.info("Enhanced Memory Manager initialized")
    
    def init_database(self):
        """Initialize the SQLite database for memory storage."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP,
                preferences TEXT
            )
            ''')
            
            # Create conversations table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                user_id TEXT,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP,
                summary TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            ''')
            
            # Create messages table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                conversation_id TEXT,
                user_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                embedding_id TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            ''')
            
            # Create facts table for long-term memory
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS facts (
                fact_id TEXT PRIMARY KEY,
                user_id TEXT,
                content TEXT,
                source TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                category TEXT,
                embedding_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            ''')
            
            # Create embeddings table for semantic search
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                embedding_id TEXT PRIMARY KEY,
                vector BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create preferences table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                preference_id TEXT PRIMARY KEY,
                user_id TEXT,
                category TEXT,
                key TEXT,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, category, key)
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Memory database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing memory database: {e}")
            raise
    
    def _encrypt(self, data: str) -> str:
        """
        Encrypt sensitive data.
        
        Args:
            data (str): Data to encrypt
            
        Returns:
            str: Encrypted data
        """
        if not data:
            return data
            
        # Simple encryption for demonstration
        # In a production environment, use a proper encryption library
        key = hashlib.sha256(self.encryption_key.encode()).digest()
        encrypted = []
        for i, c in enumerate(data):
            key_c = key[i % len(key)]
            encrypted.append(chr((ord(c) + key_c) % 65536))
        return ''.join(encrypted)
    
    def _decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data (str): Encrypted data
            
        Returns:
            str: Decrypted data
        """
        if not encrypted_data:
            return encrypted_data
            
        # Simple decryption for demonstration
        key = hashlib.sha256(self.encryption_key.encode()).digest()
        decrypted = []
        for i, c in enumerate(encrypted_data):
            key_c = key[i % len(key)]
            decrypted.append(chr((ord(c) - key_c) % 65536))
        return ''.join(decrypted)
    
    def create_user(self, name: str = None) -> str:
        """
        Create a new user.
        
        Args:
            name (str, optional): User name
            
        Returns:
            str: User ID
        """
        try:
            user_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO users (user_id, name, created_at, last_active) VALUES (?, ?, ?, ?)",
                (user_id, name, now, now)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Created new user: {user_id}")
            return user_id
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get user information.
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: User information
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id, name, created_at, last_active, preferences FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if not row:
                return None
                
            user_info = {
                "user_id": row[0],
                "name": row[1],
                "created_at": row[2],
                "last_active": row[3]
            }
            
            # Parse preferences if available
            if row[4]:
                try:
                    user_info["preferences"] = json.loads(self._decrypt(row[4]))
                except:
                    user_info["preferences"] = {}
            else:
                user_info["preferences"] = {}
            
            return user_info
            
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def update_user_activity(self, user_id: str):
        """
        Update user's last active timestamp.
        
        Args:
            user_id (str): User ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute(
                "UPDATE users SET last_active = ? WHERE user_id = ?",
                (now, user_id)
            )
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating user activity for {user_id}: {e}")
    
    def create_conversation(self, user_id: str, title: str = None) -> str:
        """
        Create a new conversation.
        
        Args:
            user_id (str): User ID
            title (str, optional): Conversation title
            
        Returns:
            str: Conversation ID
        """
        try:
            conversation_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO conversations (conversation_id, user_id, title, created_at, last_updated) VALUES (?, ?, ?, ?, ?)",
                (conversation_id, user_id, title or "New Conversation", now, now)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Created new conversation: {conversation_id} for user: {user_id}")
            return conversation_id
            
        except Exception as e:
            logger.error(f"Error creating conversation for user {user_id}: {e}")
            raise
    
    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get conversation information.
        
        Args:
            conversation_id (str): Conversation ID
            
        Returns:
            dict: Conversation information
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT conversation_id, user_id, title, created_at, last_updated, summary FROM conversations WHERE conversation_id = ?",
                (conversation_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return None
                
            conversation = {
                "conversation_id": row[0],
                "user_id": row[1],
                "title": row[2],
                "created_at": row[3],
                "last_updated": row[4],
                "summary": row[5]
            }
            
            # Get messages for this conversation
            cursor.execute(
                "SELECT message_id, role, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY timestamp",
                (conversation_id,)
            )
            
            messages = []
            for msg_row in cursor.fetchall():
                messages.append({
                    "message_id": msg_row[0],
                    "role": msg_row[1],
                    "content": msg_row[2],
                    "timestamp": msg_row[3]
                })
            
            conversation["messages"] = messages
            
            conn.close()
            return conversation
            
        except Exception as e:
            logger.error(f"Error getting conversation {conversation_id}: {e}")
            return None
    
    def get_user_conversations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get a list of conversations for a user.
        
        Args:
            user_id (str): User ID
            limit (int, optional): Maximum number of conversations to return
            
        Returns:
            list: List of conversation information
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT conversation_id, title, created_at, last_updated, summary FROM conversations WHERE user_id = ? ORDER BY last_updated DESC LIMIT ?",
                (user_id, limit)
            )
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    "conversation_id": row[0],
                    "title": row[1],
                    "created_at": row[2],
                    "last_updated": row[3],
                    "summary": row[4]
                })
            
            conn.close()
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting conversations for user {user_id}: {e}")
            return []
    
    def add_message(self, conversation_id: str, user_id: str, role: str, content: str) -> str:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id (str): Conversation ID
            user_id (str): User ID
            role (str): Message role (user, assistant, system)
            content (str): Message content
            
        Returns:
            str: Message ID
        """
        try:
            message_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            # Add the message
            cursor.execute(
                "INSERT INTO messages (message_id, conversation_id, user_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (message_id, conversation_id, user_id, role, content, now)
            )
            
            # Update conversation last_updated
            cursor.execute(
                "UPDATE conversations SET last_updated = ? WHERE conversation_id = ?",
                (now, conversation_id)
            )
            
            # Update user last_active
            cursor.execute(
                "UPDATE users SET last_active = ? WHERE user_id = ?",
                (now, user_id)
            )
            
            conn.commit()
            
            # Check if we need to update the conversation title
            if role == "user" and not cursor.execute("SELECT title FROM conversations WHERE conversation_id = ?", (conversation_id,)).fetchone()[0]:
                # Generate a title from the first user message
                title = content[:50] + "..." if len(content) > 50 else content
                cursor.execute(
                    "UPDATE conversations SET title = ? WHERE conversation_id = ?",
                    (title, conversation_id)
                )
                conn.commit()
            
            conn.close()
            
            # Extract and store facts from the message
            if role == "user":
                self._extract_facts(user_id, content, source=f"conversation:{conversation_id}")
            
            return message_id
            
        except Exception as e:
            logger.error(f"Error adding message to conversation {conversation_id}: {e}")
            raise
    
    def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get messages from a conversation.
        
        Args:
            conversation_id (str): Conversation ID
            limit (int, optional): Maximum number of messages to return
            
        Returns:
            list: List of messages
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT message_id, user_id, role, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY timestamp DESC LIMIT ?",
                (conversation_id, limit)
            )
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    "message_id": row[0],
                    "user_id": row[1],
                    "role": row[2],
                    "content": row[3],
                    "timestamp": row[4]
                })
            
            conn.close()
            
            # Return in chronological order
            return list(reversed(messages))
            
        except Exception as e:
            logger.error(f"Error getting messages for conversation {conversation_id}: {e}")
            return []
    
    def summarize_conversation(self, conversation_id: str, ai_engine=None) -> str:
        """
        Generate or update a summary for a conversation.
        
        Args:
            conversation_id (str): Conversation ID
            ai_engine (AIEngine, optional): AI engine for generating summary
            
        Returns:
            str: Conversation summary
        """
        try:
            # Get the conversation messages
            messages = self.get_conversation_messages(conversation_id)
            
            if not messages:
                return ""
            
            # Generate summary
            summary = ""
            
            if ai_engine:
                # Prepare the conversation text
                conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
                
                # Generate summary using AI
                system_message = "You are a summarization assistant. Create a concise summary of the following conversation."
                summary = ai_engine.generate_response(conversation_text, system_message=system_message)
            else:
                # Simple summary based on first user message
                for msg in messages:
                    if msg["role"] == "user":
                        summary = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                        break
            
            # Store the summary
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE conversations SET summary = ? WHERE conversation_id = ?",
                (summary, conversation_id)
            )
            
            conn.commit()
            conn.close()
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing conversation {conversation_id}: {e}")
            return ""
    
    def add_fact(self, user_id: str, content: str, source: str = None, confidence: float = 1.0, category: str = None) -> str:
        """
        Add a fact to a user's long-term memory.
        
        Args:
            user_id (str): User ID
            content (str): Fact content
            source (str, optional): Source of the fact
            confidence (float, optional): Confidence score (0-1)
            category (str, optional): Fact category
            
        Returns:
            str: Fact ID
        """
        try:
            fact_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute(
                "INSERT INTO facts (fact_id, user_id, content, source, confidence, created_at, last_accessed, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (fact_id, user_id, content, source, confidence, now, now, category)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Added fact {fact_id} for user {user_id}")
            return fact_id
            
        except Exception as e:
            logger.error(f"Error adding fact for user {user_id}: {e}")
            raise
    
    def get_facts(self, user_id: str, category: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get facts from a user's long-term memory.
        
        Args:
            user_id (str): User ID
            category (str, optional): Filter by category
            limit (int, optional): Maximum number of facts to return
            
        Returns:
            list: List of facts
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if category:
                cursor.execute(
                    "SELECT fact_id, content, source, confidence, created_at, last_accessed, access_count, category FROM facts WHERE user_id = ? AND category = ? ORDER BY last_accessed DESC LIMIT ?",
                    (user_id, category, limit)
                )
            else:
                cursor.execute(
                    "SELECT fact_id, content, source, confidence, created_at, last_accessed, access_count, category FROM facts WHERE user_id = ? ORDER BY last_accessed DESC LIMIT ?",
                    (user_id, limit)
                )
            
            facts = []
            for row in cursor.fetchall():
                facts.append({
                    "fact_id": row[0],
                    "content": row[1],
                    "source": row[2],
                    "confidence": row[3],
                    "created_at": row[4],
                    "last_accessed": row[5],
                    "access_count": row[6],
                    "category": row[7]
                })
            
            conn.close()
            return facts
            
        except Exception as e:
            logger.error(f"Error getting facts for user {user_id}: {e}")
            return []
    
    def search_facts(self, user_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for facts in a user's long-term memory.
        
        Args:
            user_id (str): User ID
            query (str): Search query
            limit (int, optional): Maximum number of facts to return
            
        Returns:
            list: List of matching facts
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Simple text search
            # In a production environment, use a vector database or embedding search
            search_term = f"%{query}%"
            cursor.execute(
                "SELECT fact_id, content, source, confidence, category FROM facts WHERE user_id = ? AND content LIKE ? ORDER BY confidence DESC LIMIT ?",
                (user_id, search_term, limit)
            )
            
            facts = []
            for row in cursor.fetchall():
                facts.append({
                    "fact_id": row[0],
                    "content": row[1],
                    "source": row[2],
                    "confidence": row[3],
                    "category": row[4]
                })
            
            # Update access counts and timestamps for retrieved facts
            for fact in facts:
                cursor.execute(
                    "UPDATE facts SET last_accessed = ?, access_count = access_count + 1 WHERE fact_id = ?",
                    (datetime.now().isoformat(), fact["fact_id"])
                )
            
            conn.commit()
            conn.close()
            return facts
            
        except Exception as e:
            logger.error(f"Error searching facts for user {user_id}: {e}")
            return []
    
    def _extract_facts(self, user_id: str, text: str, source: str = None) -> List[str]:
        """
        Extract facts from text and store them in long-term memory.
        
        Args:
            user_id (str): User ID
            text (str): Text to extract facts from
            source (str, optional): Source of the facts
            
        Returns:
            list: List of extracted fact IDs
        """
        # This is a placeholder for a more sophisticated fact extraction system
        # In a real implementation, this would use NLP to extract meaningful facts
        
        # For now, we'll just store sentences that might be facts
        fact_ids = []
        
        # Simple sentence splitting
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        
        for sentence in sentences:
            # Check if the sentence might contain a fact
            # This is a very simple heuristic
            if any(keyword in sentence.lower() for keyword in ["i am", "my name", "i like", "i prefer", "i need", "i want"]):
                fact_id = self.add_fact(
                    user_id=user_id,
                    content=sentence,
                    source=source,
                    confidence=0.7,
                    category="personal"
                )
                fact_ids.append(fact_id)
        
        return fact_ids
    
    def set_preference(self, user_id: str, category: str, key: str, value: Any) -> bool:
        """
        Set a user preference.
        
        Args:
            user_id (str): User ID
            category (str): Preference category
            key (str): Preference key
            value (Any): Preference value
            
        Returns:
            bool: Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            # Convert value to JSON string
            value_str = json.dumps(value)
            
            # Check if preference already exists
            cursor.execute(
                "SELECT preference_id FROM preferences WHERE user_id = ? AND category = ? AND key = ?",
                (user_id, category, key)
            )
            
            if cursor.fetchone():
                # Update existing preference
                cursor.execute(
                    "UPDATE preferences SET value = ?, last_updated = ? WHERE user_id = ? AND category = ? AND key = ?",
                    (value_str, now, user_id, category, key)
                )
            else:
                # Insert new preference
                preference_id = str(uuid.uuid4())
                cursor.execute(
                    "INSERT INTO preferences (preference_id, user_id, category, key, value, created_at, last_updated) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (preference_id, user_id, category, key, value_str, now, now)
                )
            
            # Also update the preferences JSON in the users table
            self._update_user_preferences_json(cursor, user_id)
            
            conn.commit()
            conn.close()
            
            # Update cache
            cache_key = f"{user_id}:{category}:{key}"
            with self.cache_lock:
                self.memory_cache[cache_key] = value
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting preference for user {user_id}: {e}")
            return False
    
    def get_preference(self, user_id: str, category: str, key: str, default: Any = None) -> Any:
        """
        Get a user preference.
        
        Args:
            user_id (str): User ID
            category (str): Preference category
            key (str): Preference key
            default (Any, optional): Default value if preference not found
            
        Returns:
            Any: Preference value
        """
        try:
            # Check cache first
            cache_key = f"{user_id}:{category}:{key}"
            with self.cache_lock:
                if cache_key in self.memory_cache:
                    return self.memory_cache[cache_key]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT value FROM preferences WHERE user_id = ? AND category = ? AND key = ?",
                (user_id, category, key)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                try:
                    value = json.loads(row[0])
                    
                    # Update cache
                    with self.cache_lock:
                        self.memory_cache[cache_key] = value
                    
                    return value
                except:
                    return default
            else:
                return default
            
        except Exception as e:
            logger.error(f"Error getting preference for user {user_id}: {e}")
            return default
    
    def get_all_preferences(self, user_id: str, category: str = None) -> Dict[str, Any]:
        """
        Get all preferences for a user.
        
        Args:
            user_id (str): User ID
            category (str, optional): Filter by category
            
        Returns:
            dict: Dictionary of preferences
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if category:
                cursor.execute(
                    "SELECT category, key, value FROM preferences WHERE user_id = ? AND category = ?",
                    (user_id, category)
                )
            else:
                cursor.execute(
                    "SELECT category, key, value FROM preferences WHERE user_id = ?",
                    (user_id,)
                )
            
            preferences = {}
            for row in cursor.fetchall():
                cat, key, value_str = row
                
                if cat not in preferences:
                    preferences[cat] = {}
                
                try:
                    preferences[cat][key] = json.loads(value_str)
                except:
                    preferences[cat][key] = value_str
            
            conn.close()
            return preferences
            
        except Exception as e:
            logger.error(f"Error getting preferences for user {user_id}: {e}")
            return {}
    
    def _update_user_preferences_json(self, cursor, user_id: str):
        """
        Update the preferences JSON in the users table.
        
        Args:
            cursor: Database cursor
            user_id (str): User ID
        """
        # Get all preferences
        cursor.execute(
            "SELECT category, key, value FROM preferences WHERE user_id = ?",
            (user_id,)
        )
        
        preferences = {}
        for row in cursor.fetchall():
            cat, key, value_str = row
            
            if cat not in preferences:
                preferences[cat] = {}
            
            try:
                preferences[cat][key] = json.loads(value_str)
            except:
                preferences[cat][key] = value_str
        
        # Encrypt and store
        preferences_json = json.dumps(preferences)
        encrypted_preferences = self._encrypt(preferences_json)
        
        cursor.execute(
            "UPDATE users SET preferences = ? WHERE user_id = ?",
            (encrypted_preferences, user_id)
        )
    
    def get_context(self, user_id: str, conversation_id: str = None, context_window: int = 10) -> Dict[str, Any]:
        """
        Get context for a conversation, including recent messages and relevant facts.
        
        Args:
            user_id (str): User ID
            conversation_id (str, optional): Conversation ID
            context_window (int, optional): Number of recent messages to include
            
        Returns:
            dict: Context information
        """
        context = {
            "user": self.get_user(user_id),
            "preferences": self.get_all_preferences(user_id),
            "recent_messages": [],
            "relevant_facts": []
        }
        
        # Get recent messages if conversation_id is provided
        if conversation_id:
            context["recent_messages"] = self.get_conversation_messages(conversation_id, limit=context_window)
            
            # Extract query from recent messages
            query = ""
            for msg in reversed(context["recent_messages"]):
                if msg["role"] == "user":
                    query = msg["content"]
                    break
            
            # Get relevant facts based on recent messages
            if query:
                context["relevant_facts"] = self.search_facts(user_id, query, limit=5)
        
        return context
    
    def clear_user_data(self, user_id: str) -> bool:
        """
        Clear all data for a user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            bool: Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete messages
            cursor.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
            
            # Delete conversations
            cursor.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
            
            # Delete facts
            cursor.execute("DELETE FROM facts WHERE user_id = ?", (user_id,))
            
            # Delete preferences
            cursor.execute("DELETE FROM preferences WHERE user_id = ?", (user_id,))
            
            # Update user
            cursor.execute("UPDATE users SET preferences = NULL WHERE user_id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            
            # Clear cache for this user
            with self.cache_lock:
                keys_to_remove = [k for k in self.memory_cache if k.startswith(f"{user_id}:")]
                for key in keys_to_remove:
                    del self.memory_cache[key]
            
            logger.info(f"Cleared all data for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing data for user {user_id}: {e}")
            return False
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all data for a user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: User data
        """
        try:
            user_data = {
                "user": self.get_user(user_id),
                "preferences": self.get_all_preferences(user_id),
                "conversations": [],
                "facts": self.get_facts(user_id, limit=1000)
            }
            
            # Get all conversations
            conversations = self.get_user_conversations(user_id, limit=1000)
            
            for conv in conversations:
                conv_data = self.get_conversation(conv["conversation_id"])
                if conv_data:
                    user_data["conversations"].append(conv_data)
            
            return user_data
            
        except Exception as e:
            logger.error(f"Error exporting data for user {user_id}: {e}")
            return {"error": str(e)}
    
    def import_user_data(self, user_data: Dict[str, Any]) -> str:
        """
        Import user data.
        
        Args:
            user_data (dict): User data to import
            
        Returns:
            str: User ID
        """
        try:
            # Create a new user
            user_id = self.create_user(user_data.get("user", {}).get("name"))
            
            # Import preferences
            for category, prefs in user_data.get("preferences", {}).items():
                for key, value in prefs.items():
                    self.set_preference(user_id, category, key, value)
            
            # Import facts
            for fact in user_data.get("facts", []):
                self.add_fact(
                    user_id=user_id,
                    content=fact.get("content", ""),
                    source=fact.get("source"),
                    confidence=fact.get("confidence", 1.0),
                    category=fact.get("category")
                )
            
            # Import conversations
            for conv in user_data.get("conversations", []):
                conv_id = self.create_conversation(user_id, conv.get("title"))
                
                for msg in conv.get("messages", []):
                    self.add_message(
                        conversation_id=conv_id,
                        user_id=user_id,
                        role=msg.get("role", "user"),
                        content=msg.get("content", "")
                    )
            
            return user_id
            
        except Exception as e:
            logger.error(f"Error importing user data: {e}")
            raise
