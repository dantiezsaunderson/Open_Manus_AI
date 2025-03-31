import os
import sys
import logging
from dotenv import load_dotenv

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

def main():
    """Main entry point for the application."""
    logger.info("Starting Open Manus AI...")
    
    try:
        # Import and run the Streamlit app
        logger.info("Launching Streamlit interface...")
        os.system("streamlit run src/streamlit_app.py")
        
    except Exception as e:
        logger.error(f"Error starting Open Manus AI: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
