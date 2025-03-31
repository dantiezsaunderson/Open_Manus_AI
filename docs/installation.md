# Installation Guide

## Prerequisites

Before installing Open Manus AI, ensure you have the following prerequisites:

- Python 3.10 or higher
- Git
- Docker and Docker Compose (for containerized deployment)
- API keys for the following services:
  - OpenAI API
  - Alpha Vantage (financial data)
  - Finnhub (financial data)
  - OpenWeather API
  - News API
  - GitHub (for repository management)
  - Render (for deployment)
  - Telegram Bot API

## Method 1: Local Installation

Follow these steps to install Open Manus AI locally:

1. **Clone the repository**

   ```bash
   git clone https://github.com/dantiezsaunderson/Open_Manus_AI.git
   cd Open_Manus_AI
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file with your API keys and configuration:

   ```
   # OpenAI API
   OPENAI_API_KEY=your_openai_api_key

   # Financial APIs
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
   FINNHUB_API_KEY=your_finnhub_key

   # Weather API
   OPENWEATHER_API_KEY=your_openweather_key

   # News API
   NEWSAPI_KEY=your_newsapi_key

   # GitHub Integration
   GITHUB_TOKEN=your_github_token

   # Render Integration
   RENDER_API_KEY=your_render_api_key
   RENDER_DEPLOY_HOOK=your_render_deploy_hook_url

   # Telegram Bot
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   ```

5. **Run the application**

   To start the main application with Streamlit dashboard:

   ```bash
   python -m src.main
   ```

   To start only the Streamlit dashboard:

   ```bash
   python -m src.interfaces.streamlit_app
   ```

   To start only the Telegram bot:

   ```bash
   python -m src.interfaces.telegram_bot
   ```

## Method 2: Docker Installation

For containerized deployment, follow these steps:

1. **Clone the repository**

   ```bash
   git clone https://github.com/dantiezsaunderson/Open_Manus_AI.git
   cd Open_Manus_AI
   ```

2. **Set up environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file with your API keys and configuration as shown above.

3. **Build and run with Docker Compose**

   ```bash
   docker-compose up -d
   ```

   This will start both the main application with Streamlit dashboard and the Telegram bot.

4. **Access the application**

   Open your browser and navigate to:
   - Streamlit dashboard: http://localhost:8501

## Troubleshooting

### Common Issues

1. **API Key Issues**

   If you encounter errors related to API access, verify that:
   - All required API keys are correctly set in the `.env` file
   - API keys are valid and have not expired
   - You have sufficient quota/credits for the APIs you're using

2. **Docker Issues**

   If you encounter Docker-related errors:
   - Ensure Docker and Docker Compose are correctly installed
   - Check if the required ports (8501) are available
   - Verify that you have sufficient permissions to run Docker commands

3. **Python Environment Issues**

   If you encounter Python-related errors:
   - Verify that you're using Python 3.10 or higher
   - Ensure all dependencies are correctly installed
   - Check if your virtual environment is activated

### Getting Help

If you encounter issues not covered in this guide:

1. Check the [documentation](documentation.md) for more detailed information
2. Look for similar issues in the GitHub repository's Issues section
3. Create a new issue on GitHub with details about your problem
