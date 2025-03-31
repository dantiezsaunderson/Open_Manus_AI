"""
Memory Manager Module

This module handles the secure storage and retrieval of user memory and context
for personalized interactions in Open Manus AI.
"""

import os
import json
import logging
import datetime
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Memory Manager class that handles secure storage and retrieval of user data.
    """
    
    def __init__(self, storage_dir=None):
        """
        Initialize the Memory Manager with storage location.
        
        Args:
            storage_dir (str, optional): Directory to store memory data
        """
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path.home() / ".open_manus_ai" / "memory"
        
        # Create storage directory if it doesn't exist
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize memory cache
        self.memory_cache = {}
        
        logger.info(f"Memory Manager initialized with storage at {self.storage_dir}")
    
    def save_memory(self, user_id, key, value):
        """
        Save a memory item for a specific user.
        
        Args:
            user_id (str): Unique identifier for the user
            key (str): Memory item key
            value (any): Memory item value (must be JSON serializable)
            
        Returns:
            bool: Success status
        """
        try:
            # Create user directory if it doesn't exist
            user_dir = self.storage_dir / user_id
            user_dir.mkdir(exist_ok=True)
            
            # Load existing memory file if it exists
            memory_file = user_dir / "memory.json"
            if memory_file.exists():
                with open(memory_file, "r") as f:
                    memory_data = json.load(f)
            else:
                memory_data = {}
            
            # Update memory with new value
            memory_data[key] = {
                "value": value,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Save updated memory
            with open(memory_file, "w") as f:
                json.dump(memory_data, f, indent=2)
            
            # Update cache
            if user_id not in self.memory_cache:
                self.memory_cache[user_id] = {}
            self.memory_cache[user_id][key] = value
            
            logger.debug(f"Memory saved for user {user_id}: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving memory for user {user_id}: {e}")
            return False
    
    def get_memory(self, user_id, key, default=None):
        """
        Retrieve a memory item for a specific user.
        
        Args:
            user_id (str): Unique identifier for the user
            key (str): Memory item key
            default (any, optional): Default value if memory item doesn't exist
            
        Returns:
            any: The memory item value or default if not found
        """
        # Check cache first
        if user_id in self.memory_cache and key in self.memory_cache[user_id]:
            return self.memory_cache[user_id][key]
        
        try:
            # Check if user memory file exists
            memory_file = self.storage_dir / user_id / "memory.json"
            if not memory_file.exists():
                return default
            
            # Load memory data
            with open(memory_file, "r") as f:
                memory_data = json.load(f)
            
            # Get memory item if it exists
            if key in memory_data:
                value = memory_data[key]["value"]
                
                # Update cache
                if user_id not in self.memory_cache:
                    self.memory_cache[user_id] = {}
                self.memory_cache[user_id][key] = value
                
                return value
            else:
                return default
                
        except Exception as e:
            logger.error(f"Error retrieving memory for user {user_id}: {e}")
            return default
    
    def delete_memory(self, user_id, key=None):
        """
        Delete a memory item or all memory for a specific user.
        
        Args:
            user_id (str): Unique identifier for the user
            key (str, optional): Memory item key to delete, or None to delete all
            
        Returns:
            bool: Success status
        """
        try:
            memory_file = self.storage_dir / user_id / "memory.json"
            
            # If key is None, delete all memory for the user
            if key is None:
                if memory_file.exists():
                    memory_file.unlink()
                
                # Clear cache for user
                if user_id in self.memory_cache:
                    del self.memory_cache[user_id]
                
                logger.info(f"All memory deleted for user {user_id}")
                return True
            
            # Otherwise, delete specific memory item
            if not memory_file.exists():
                return False
            
            # Load memory data
            with open(memory_file, "r") as f:
                memory_data = json.load(f)
            
            # Remove memory item if it exists
            if key in memory_data:
                del memory_data[key]
                
                # Save updated memory
                with open(memory_file, "w") as f:
                    json.dump(memory_data, f, indent=2)
                
                # Update cache
                if user_id in self.memory_cache and key in self.memory_cache[user_id]:
                    del self.memory_cache[user_id][key]
                
                logger.debug(f"Memory item {key} deleted for user {user_id}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error deleting memory for user {user_id}: {e}")
            return False
    
    def get_all_memory(self, user_id):
        """
        Retrieve all memory items for a specific user.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            dict: All memory items for the user
        """
        try:
            memory_file = self.storage_dir / user_id / "memory.json"
            if not memory_file.exists():
                return {}
            
            # Load memory data
            with open(memory_file, "r") as f:
                memory_data = json.load(f)
            
            # Extract just the values (not timestamps)
            result = {k: v["value"] for k, v in memory_data.items()}
            
            # Update cache
            self.memory_cache[user_id] = result
            
            return result
                
        except Exception as e:
            logger.error(f"Error retrieving all memory for user {user_id}: {e}")
            return {}
