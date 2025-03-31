#!/usr/bin/env python3
"""
Open Manus AI - Main Entry Point

This module serves as the main entry point for the Open Manus AI application.
It initializes all components and starts the appropriate interface based on configuration.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("open_manus_ai.log")
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def initialize_components():
    """Initialize all required components for the application."""
    from src.core.ai_engine import AIEngine
    from src.core.memory_manager import MemoryManager
    from src.modules.conversation import ConversationModule
    from src.modules.task_automation import TaskAutomationModule
    from src.modules.coding_support import CodingSupportModule
    from src.modules.financial_analysis import FinancialAnalysisModule
    from src.modules.multi_agent import MultiAgentSystem
    
    logger.info("Initializing Open Manus AI components...")
    
    # Initialize core components
    memory_manager = MemoryManager()
    ai_engine = AIEngine()
    
    # Initialize modules
    conversation_module = ConversationModule(ai_engine, memory_manager)
    task_automation = TaskAutomationModule(ai_engine, memory_manager)
    coding_support = CodingSupportModule(ai_engine)
    financial_analysis = FinancialAnalysisModule()
    multi_agent_system = MultiAgentSystem(ai_engine)
    
    components = {
        "ai_engine": ai_engine,
        "memory_manager": memory_manager,
        "conversation": conversation_module,
        "task_automation": task_automation,
        "coding_support": coding_support,
        "financial_analysis": financial_analysis,
        "multi_agent": multi_agent_system
    }
    
    logger.info("All components initialized successfully")
    return components

def start_interface(components, interface_type="cli"):
    """Start the specified user interface."""
    logger.info(f"Starting {interface_type} interface...")
    
    if interface_type == "streamlit":
        # Streamlit interface is started separately via the streamlit command
        logger.info("To start the Streamlit interface, run: streamlit run src/interfaces/streamlit_app.py")
    elif interface_type == "telegram":
        from src.interfaces.telegram_bot import start_bot
        start_bot(components)
    else:  # Default to CLI
        from src.interfaces.cli import start_cli
        start_cli(components)

def main():
    """Main entry point for the application."""
    logger.info("Starting Open Manus AI...")
    
    try:
        # Initialize all components
        components = initialize_components()
        
        # Determine which interface to start
        interface_type = os.getenv("INTERFACE_TYPE", "cli").lower()
        start_interface(components, interface_type)
        
    except Exception as e:
        logger.error(f"Error starting Open Manus AI: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
