"""
Task Automation Module

This module handles automated task execution and scheduling for
the Open Manus AI system.
"""

import logging
import datetime
import asyncio
import threading
from queue import Queue

# Configure logging
logger = logging.getLogger(__name__)

class TaskAutomationModule:
    """
    Task Automation Module for handling automated task execution.
    """
    
    def __init__(self, ai_engine, memory_manager):
        """
        Initialize the Task Automation Module.
        
        Args:
            ai_engine (AIEngine): The AI engine instance
            memory_manager (MemoryManager): The memory manager instance
        """
        self.ai_engine = ai_engine
        self.memory_manager = memory_manager
        self.task_queue = Queue()
        self.scheduled_tasks = []
        self.running = False
        self.worker_thread = None
        logger.info("Task Automation Module initialized")
    
    def start(self):
        """Start the task automation worker thread."""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._task_worker, daemon=True)
            self.worker_thread.start()
            logger.info("Task automation worker started")
    
    def stop(self):
        """Stop the task automation worker thread."""
        if self.running:
            self.running = False
            if self.worker_thread:
                self.worker_thread.join(timeout=2.0)
            logger.info("Task automation worker stopped")
    
    def _task_worker(self):
        """Worker thread function to process tasks."""
        while self.running:
            try:
                # Check for scheduled tasks
                now = datetime.datetime.now()
                for task in list(self.scheduled_tasks):
                    if now >= task["scheduled_time"]:
                        self.task_queue.put(task["task"])
                        self.scheduled_tasks.remove(task)
                        logger.info(f"Scheduled task added to queue: {task['task']['name']}")
                
                # Process task queue
                if not self.task_queue.empty():
                    task = self.task_queue.get()
                    logger.info(f"Processing task: {task['name']}")
                    
                    try:
                        result = self._execute_task(task)
                        logger.info(f"Task completed: {task['name']}, result: {result}")
                        
                        # Store task result in memory if user_id is provided
                        if "user_id" in task and task["user_id"]:
                            task_history = self.memory_manager.get_memory(
                                task["user_id"], "task_history", []
                            )
                            task_history.append({
                                "task": task,
                                "result": result,
                                "timestamp": datetime.datetime.now().isoformat()
                            })
                            self.memory_manager.save_memory(
                                task["user_id"], "task_history", task_history
                            )
                    except Exception as e:
                        logger.error(f"Error executing task {task['name']}: {e}")
                    
                    self.task_queue.task_done()
                else:
                    # Sleep briefly to avoid busy waiting
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error in task worker: {e}")
                time.sleep(1)  # Avoid rapid error loops
    
    def _execute_task(self, task):
        """
        Execute a task based on its type.
        
        Args:
            task (dict): Task definition
            
        Returns:
            dict: Task execution result
        """
        task_type = task.get("type", "unknown")
        
        if task_type == "reminder":
            return self._execute_reminder_task(task)
        elif task_type == "data_fetch":
            return self._execute_data_fetch_task(task)
        elif task_type == "analysis":
            return self._execute_analysis_task(task)
        elif task_type == "custom":
            return self._execute_custom_task(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    def _execute_reminder_task(self, task):
        """Execute a reminder task."""
        # Implementation details would depend on notification system
        return {"status": "completed", "message": task.get("message", "Reminder!")}
    
    def _execute_data_fetch_task(self, task):
        """Execute a data fetch task."""
        # Implementation would depend on data sources
        return {"status": "completed", "data": {"sample": "data"}}
    
    def _execute_analysis_task(self, task):
        """Execute an analysis task using the AI engine."""
        data = task.get("data", "")
        analysis_type = task.get("analysis_type", "general")
        
        if analysis_type == "financial":
            result = self.ai_engine.analyze_financial_data(data)
        elif analysis_type == "code":
            result = self.ai_engine.analyze_code(data, task.get("language", "python"))
        else:
            # General analysis
            system_message = "Analyze the following data and provide insights."
            result = {"analysis": self.ai_engine.generate_response(data, system_message=system_message)}
        
        return {"status": "completed", "result": result}
    
    def _execute_custom_task(self, task):
        """Execute a custom task defined by a function."""
        if "function" in task and callable(task["function"]):
            args = task.get("args", [])
            kwargs = task.get("kwargs", {})
            result = task["function"](*args, **kwargs)
            return {"status": "completed", "result": result}
        else:
            return {"status": "error", "message": "No callable function provided"}
    
    def add_task(self, task):
        """
        Add a task to the queue for immediate execution.
        
        Args:
            task (dict): Task definition with at least 'name' and 'type' keys
            
        Returns:
            bool: Success status
        """
        try:
            if not isinstance(task, dict) or "name" not in task or "type" not in task:
                logger.error("Invalid task format")
                return False
            
            self.task_queue.put(task)
            logger.info(f"Task added to queue: {task['name']}")
            return True
        except Exception as e:
            logger.error(f"Error adding task: {e}")
            return False
    
    def schedule_task(self, task, scheduled_time):
        """
        Schedule a task for future execution.
        
        Args:
            task (dict): Task definition with at least 'name' and 'type' keys
            scheduled_time (datetime): When to execute the task
            
        Returns:
            bool: Success status
        """
        try:
            if not isinstance(task, dict) or "name" not in task or "type" not in task:
                logger.error("Invalid task format")
                return False
            
            if not isinstance(scheduled_time, datetime.datetime):
                logger.error("scheduled_time must be a datetime object")
                return False
            
            self.scheduled_tasks.append({
                "task": task,
                "scheduled_time": scheduled_time
            })
            
            logger.info(f"Task scheduled: {task['name']} at {scheduled_time}")
            return True
        except Exception as e:
            logger.error(f"Error scheduling task: {e}")
            return False
    
    def get_pending_tasks(self, user_id=None):
        """
        Get all pending tasks, optionally filtered by user_id.
        
        Args:
            user_id (str, optional): Filter tasks by user ID
            
        Returns:
            list: List of pending tasks
        """
        pending = []
        
        # Get tasks from queue
        queue_tasks = list(self.task_queue.queue)
        if user_id:
            queue_tasks = [t for t in queue_tasks if t.get("user_id") == user_id]
        pending.extend(queue_tasks)
        
        # Get scheduled tasks
        scheduled = [t["task"] for t in self.scheduled_tasks]
        if user_id:
            scheduled = [t for t in scheduled if t.get("user_id") == user_id]
        pending.extend(scheduled)
        
        return pending
