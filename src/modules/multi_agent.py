"""
Multi-Agent System Module

This module implements a collaborative multi-agent system for task delegation
and specialized processing in the Open Manus AI system.
"""

import logging
import uuid
import threading
import queue
import time

# Configure logging
logger = logging.getLogger(__name__)

class Agent:
    """Base class for specialized agents in the multi-agent system."""
    
    def __init__(self, name, agent_type, ai_engine=None):
        """
        Initialize a specialized agent.
        
        Args:
            name (str): Agent name
            agent_type (str): Type of agent (e.g., 'research', 'coding', 'financial')
            ai_engine (AIEngine, optional): AI engine instance for the agent
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.type = agent_type
        self.ai_engine = ai_engine
        self.task_queue = queue.Queue()
        self.results = {}
        self.running = False
        self.worker_thread = None
        logger.info(f"Agent '{name}' ({agent_type}) initialized")
    
    def start(self):
        """Start the agent's worker thread."""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._process_tasks, daemon=True)
            self.worker_thread.start()
            logger.info(f"Agent '{self.name}' started")
    
    def stop(self):
        """Stop the agent's worker thread."""
        if self.running:
            self.running = False
            if self.worker_thread:
                self.worker_thread.join(timeout=2.0)
            logger.info(f"Agent '{self.name}' stopped")
    
    def assign_task(self, task):
        """
        Assign a task to this agent.
        
        Args:
            task (dict): Task definition
            
        Returns:
            str: Task ID
        """
        task_id = task.get('id', str(uuid.uuid4()))
        task['id'] = task_id
        task['status'] = 'assigned'
        task['assigned_time'] = time.time()
        
        self.task_queue.put(task)
        self.results[task_id] = {'status': 'pending'}
        
        logger.info(f"Task {task_id} assigned to agent '{self.name}'")
        return task_id
    
    def get_result(self, task_id):
        """
        Get the result of a task.
        
        Args:
            task_id (str): Task ID
            
        Returns:
            dict: Task result or status
        """
        return self.results.get(task_id, {'status': 'unknown'})
    
    def _process_tasks(self):
        """Process tasks from the queue (to be implemented by subclasses)."""
        while self.running:
            try:
                if not self.task_queue.empty():
                    task = self.task_queue.get()
                    logger.info(f"Agent '{self.name}' processing task {task['id']}")
                    
                    try:
                        # Update task status
                        task['status'] = 'processing'
                        self.results[task['id']] = {'status': 'processing'}
                        
                        # Process the task (to be implemented by subclasses)
                        result = self._execute_task(task)
                        
                        # Store the result
                        self.results[task['id']] = {
                            'status': 'completed',
                            'result': result,
                            'completion_time': time.time()
                        }
                        
                        logger.info(f"Agent '{self.name}' completed task {task['id']}")
                        
                    except Exception as e:
                        logger.error(f"Error processing task {task['id']}: {e}")
                        self.results[task['id']] = {
                            'status': 'failed',
                            'error': str(e),
                            'completion_time': time.time()
                        }
                    
                    self.task_queue.task_done()
                else:
                    # Sleep briefly to avoid busy waiting
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error in agent '{self.name}' task processing: {e}")
                time.sleep(1)  # Avoid rapid error loops
    
    def _execute_task(self, task):
        """
        Execute a task (to be implemented by subclasses).
        
        Args:
            task (dict): Task definition
            
        Returns:
            dict: Task execution result
        """
        raise NotImplementedError("Subclasses must implement _execute_task")


class ResearchAgent(Agent):
    """Specialized agent for research and information gathering."""
    
    def __init__(self, ai_engine):
        """Initialize a research agent."""
        super().__init__("Research Agent", "research", ai_engine)
    
    def _execute_task(self, task):
        """Execute a research task."""
        task_type = task.get('task_type', 'general')
        query = task.get('query', '')
        
        if not query:
            return {'error': 'No query provided'}
        
        if task_type == 'summarize':
            system_message = "You are a research assistant. Summarize the following information concisely but thoroughly."
            result = self.ai_engine.generate_response(query, system_message=system_message)
            return {'summary': result}
        
        elif task_type == 'analyze':
            system_message = "You are a research analyst. Analyze the following information and provide insights."
            result = self.ai_engine.generate_response(query, system_message=system_message)
            return {'analysis': result}
        
        else:  # general research
            system_message = "You are a research assistant. Provide comprehensive information on the following topic."
            result = self.ai_engine.generate_response(query, system_message=system_message)
            return {'research': result}


class CodingAgent(Agent):
    """Specialized agent for coding and software development."""
    
    def __init__(self, ai_engine):
        """Initialize a coding agent."""
        super().__init__("Coding Agent", "coding", ai_engine)
    
    def _execute_task(self, task):
        """Execute a coding task."""
        task_type = task.get('task_type', 'generate')
        language = task.get('language', 'python')
        code = task.get('code', '')
        prompt = task.get('prompt', '')
        
        if task_type == 'generate':
            if not prompt:
                return {'error': 'No prompt provided for code generation'}
            
            system_message = f"You are an expert {language} programmer. Generate clean, efficient code based on the requirements."
            result = self.ai_engine.generate_response(prompt, system_message=system_message)
            
            # Extract code from result
            import re
            code_pattern = f"```{language}(.*?)```"
            code_match = re.search(code_pattern, result, re.DOTALL)
            
            if code_match:
                extracted_code = code_match.group(1).strip()
                return {'code': extracted_code, 'explanation': result}
            else:
                return {'code': '', 'explanation': result}
        
        elif task_type == 'analyze':
            if not code:
                return {'error': 'No code provided for analysis'}
            
            system_message = f"You are a code review expert. Analyze this {language} code and provide feedback on quality, bugs, and improvements."
            result = self.ai_engine.generate_response(code, system_message=system_message)
            return {'analysis': result}
        
        elif task_type == 'refactor':
            if not code:
                return {'error': 'No code provided for refactoring'}
            
            system_message = f"You are a code refactoring expert. Improve this {language} code while maintaining its functionality."
            result = self.ai_engine.generate_response(code, system_message=system_message)
            
            # Extract code from result
            import re
            code_pattern = f"```{language}(.*?)```"
            code_match = re.search(code_pattern, result, re.DOTALL)
            
            if code_match:
                refactored_code = code_match.group(1).strip()
                return {'refactored_code': refactored_code, 'explanation': result}
            else:
                return {'refactored_code': '', 'explanation': result}
        
        else:
            return {'error': f'Unknown task type: {task_type}'}


class FinancialAgent(Agent):
    """Specialized agent for financial analysis and recommendations."""
    
    def __init__(self, ai_engine):
        """Initialize a financial agent."""
        super().__init__("Financial Agent", "financial", ai_engine)
    
    def _execute_task(self, task):
        """Execute a financial analysis task."""
        task_type = task.get('task_type', 'analyze')
        data = task.get('data', '')
        symbol = task.get('symbol', '')
        
        if task_type == 'analyze_stock':
            if not symbol:
                return {'error': 'No stock symbol provided'}
            
            # This would typically use the FinancialAnalysisModule
            # For now, we'll use the AI engine to generate an analysis
            prompt = f"Provide a comprehensive analysis of the stock {symbol}, including recent performance, technical indicators, and outlook."
            system_message = "You are a financial analyst specializing in stock market analysis."
            result = self.ai_engine.generate_response(prompt, system_message=system_message)
            return {'analysis': result}
        
        elif task_type == 'analyze_data':
            if not data:
                return {'error': 'No financial data provided'}
            
            system_message = "You are a financial data analyst. Analyze this financial data and provide insights."
            result = self.ai_engine.generate_response(data, system_message=system_message)
            return {'analysis': result}
        
        elif task_type == 'recommend':
            prompt = f"Based on current market conditions, provide investment recommendations for {data if data else 'a balanced portfolio'}."
            system_message = "You are a financial advisor providing investment recommendations."
            result = self.ai_engine.generate_response(prompt, system_message=system_message)
            return {'recommendations': result}
        
        else:
            return {'error': f'Unknown task type: {task_type}'}


class MultiAgentSystem:
    """
    Multi-Agent System for collaborative task processing.
    """
    
    def __init__(self, ai_engine):
        """
        Initialize the Multi-Agent System.
        
        Args:
            ai_engine (AIEngine): The AI engine instance
        """
        self.ai_engine = ai_engine
        self.agents = {}
        self.task_assignments = {}
        
        # Create default agents
        self.create_agent("research", ResearchAgent(ai_engine))
        self.create_agent("coding", CodingAgent(ai_engine))
        self.create_agent("financial", FinancialAgent(ai_engine))
        
        logger.info("Multi-Agent System initialized")
    
    def create_agent(self, agent_id, agent):
        """
        Add an agent to the system.
        
        Args:
            agent_id (str): Unique identifier for the agent
            agent (Agent): Agent instance
            
        Returns:
            bool: Success status
        """
        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} already exists, replacing")
        
        self.agents[agent_id] = agent
        agent.start()
        logger.info(f"Agent {agent_id} added to Multi-Agent System")
        return True
    
    def remove_agent(self, agent_id):
        """
        Remove an agent from the system.
        
        Args:
            agent_id (str): Unique identifier for the agent
            
        Returns:
            bool: Success status
        """
        if agent_id in self.agents:
            self.agents[agent_id].stop()
            del self.agents[agent_id]
            logger.info(f"Agent {agent_id} removed from Multi-Agent System")
            return True
        else:
            logger.warning(f"Agent {agent_id} not found")
            return False
    
    def assign_task(self, task, agent_id=None):
        """
        Assign a task to an agent.
        
        Args:
            task (dict): Task definition
            agent_id (str, optional): Specific agent to assign the task to
            
        Returns:
            str: Task ID
        """
        # Generate task ID if not provided
        if 'id' not in task:
            task['id'] = str(uuid.uuid4())
        
        # If no specific agent is requested, determine the best agent for the task
        if agent_id is None:
            agent_id = self._determine_best_agent(task)
        
        # Check if the agent exists
        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} not found")
            return None
        
        # Assign the task to the agent
        task_id = self.agents[agent_id].assign_task(task)
        self.task_assignments[task_id] = agent_id
        
        return task_id
    
    def get_task_result(self, task_id):
        """
        Get the result of a task.
        
        Args:
            task_id (str): Task ID
            
        Returns:
            dict: Task result or status
        """
        if task_id not in self.task_assignments:
            return {'status': 'unknown', 'error': 'Task not found'}
        
        agent_id = self.task_assignments[task_id]
        return self.agents[agent_id].get_result(task_id)
    
    def _determine_best_agent(self, task):
        """
        Determine the best agent for a given task.
        
        Args:
            task (dict): Task definition
            
        Returns:
            str: Agent ID
        """
        task_type = task.get('type', '').lower()
        
        if 'code' in task_type or 'programming' in task_type:
            return 'coding'
        elif 'research' in task_type or 'information' in task_type:
            return 'research'
        elif 'finance' in task_type or 'stock' in task_type or 'investment' in task_type:
            return 'financial'
        else:
            # Default to research agent for general tasks
            return 'research'
    
    def collaborative_task(self, main_task, subtasks=None):
        """
        Execute a collaborative task involving multiple agents.
        
        Args:
            main_task (dict): Main task definition
            subtasks (list, optional): List of subtask definitions
            
        Returns:
            dict: Collaborative task result
        """
        if subtasks is None:
            # Automatically break down the main task into subtasks
            subtasks = self._break_down_task(main_task)
        
        # Assign subtasks to appropriate agents
        subtask_ids = []
        for subtask in subtasks:
            task_id = self.assign_task(subtask)
            if task_id:
                subtask_ids.append(task_id)
        
        # Wait for all subtasks to complete
        all_completed = False
        max_wait_time = 300  # 5 minutes
        start_time = time.time()
        
        while not all_completed and time.time() - start_time < max_wait_time:
            all_completed = True
            
            for task_id in subtask_ids:
                result = self.get_task_result(task_id)
                if result['status'] not in ['completed', 'failed']:
                    all_completed = False
                    break
            
            if not all_completed:
                time.sleep(1)
        
        # Collect results
        subtask_results = {}
        for task_id in subtask_ids:
            subtask_results[task_id] = self.get_task_result(task_id)
        
        # Combine results (this could be done by another agent)
        combined_result = self._combine_results(main_task, subtask_results)
        
        return {
            'main_task': main_task,
            'subtasks': subtask_results,
            'combined_result': combined_result,
            'status': 'completed' if all_completed else 'partial'
        }
    
    def _break_down_task(self, task):
        """
        Break down a complex task into subtasks.
        
        Args:
            task (dict): Task definition
            
        Returns:
            list: List of subtask definitions
        """
        # This is a simplified implementation
        # In a real system, this could use the AI engine to intelligently break down tasks
        
        task_type = task.get('type', '').lower()
        description = task.get('description', '')
        
        if 'research' in task_type and 'report' in task_type:
            # Break down research report task
            return [
                {
                    'type': 'research',
                    'task_type': 'general',
                    'query': f"Gather background information on {description}",
                    'description': f"Background research for {description}"
                },
                {
                    'type': 'research',
                    'task_type': 'analyze',
                    'query': f"Analyze current trends related to {description}",
                    'description': f"Trend analysis for {description}"
                },
                {
                    'type': 'research',
                    'task_type': 'summarize',
                    'query': f"Summarize key findings about {description}",
                    'description': f"Summary for {description}"
                }
            ]
        elif 'code' in task_type and 'project' in task_type:
            # Break down coding project task
            return [
                {
                    'type': 'code',
                    'task_type': 'generate',
                    'language': 'python',
                    'prompt': f"Design the architecture for {description}",
                    'description': f"Architecture design for {description}"
                },
                {
                    'type': 'code',
                    'task_type': 'generate',
                    'language': 'python',
                    'prompt': f"Implement the core functionality for {description}",
                    'description': f"Core implementation for {description}"
                },
                {
                    'type': 'code',
                    'task_type': 'generate',
                    'language': 'python',
                    'prompt': f"Create tests for {description}",
                    'description': f"Test suite for {description}"
                }
            ]
        else:
            # Default breakdown for general tasks
            return [
                {
                    'type': 'research',
                    'task_type': 'general',
                    'query': description,
                    'description': f"General research for {description}"
                }
            ]
    
    def _combine_results(self, main_task, subtask_results):
        """
        Combine subtask results into a cohesive result.
        
        Args:
            main_task (dict): Main task definition
            subtask_results (dict): Results of subtasks
            
        Returns:
            dict: Combined result
        """
        # Extract results from completed subtasks
        completed_results = []
        for task_id, result in subtask_results.items():
            if result['status'] == 'completed':
                # Extract the actual result content
                if 'result' in result:
                    completed_results.append(result['result'])
        
        # If no completed results, return error
        if not completed_results:
            return {
                'status': 'failed',
                'error': 'No subtasks completed successfully'
            }
        
        # For now, just return the collection of results
        # In a real system, this could use the AI engine to synthesize a cohesive result
        return {
            'status': 'completed',
            'results': completed_results
        }
