# Installation Guide for Open Manus AI

This guide will walk you through the process of installing and setting up Open Manus AI on your local machine or server.

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.10 or higher
- Git
- Docker and Docker Compose (optional, for containerized deployment)
- API keys for:
  - OpenAI API
  - Alpha Vantage (financial data)
  - OpenWeather API
  - News API
  - Telegram Bot API (if using Telegram integration)

## Method 1: Local Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/dantiezsaunderson/Open_Manus_AI.git
cd Open_Manus_AI
```

### Step 2: Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit the `.env` file and add your API keys:

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

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

### Step 5: Run the Application

To start the main application with the Streamlit dashboard:

```bash
python -m src.main
```

The Streamlit dashboard will be available at http://localhost:8501

To run only the Telegram bot:

```bash
python -m src.interfaces.telegram_bot
```

## Method 2: Docker Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/dantiezsaunderson/Open_Manus_AI.git
cd Open_Manus_AI
```

### Step 2: Configure Environment Variables

Create a `.env` file as described in Method 1, Step 4.

### Step 3: Build and Run with Docker Compose

```bash
docker-compose up -d
```

This will start both the main application and the Telegram bot in separate containers.

The Streamlit dashboard will be available at http://localhost:8501

## Method 3: Netlify Deployment

### Step 1: Fork or Clone the Repository

First, fork the repository on GitHub or clone it and push to your own GitHub account.

### Step 2: Deploy to Netlify

1. Log in to your Netlify account
2. Click "Add new site" > "Import an existing project"
3. Select "GitHub" as the Git provider
4. Authorize Netlify to access your GitHub account if prompted
5. Select the "Open_Manus_AI" repository
6. Configure the following build settings:
   - Build command: `pip install -r requirements.txt`
   - Publish directory: `src`
   - Advanced build settings: Add the following environment variables:
     - OPENAI_API_KEY: Your OpenAI API key
     - TELEGRAM_BOT_TOKEN: Your Telegram bot token
     - Add any other API keys as needed

### Step 3: Configure Telegram Bot Webhook (if using Telegram)

After deployment, configure the Telegram bot webhook:

```bash
curl -F "url=https://your-netlify-site.netlify.app/webhook" https://api.telegram.org/bot<YOUR_TELEGRAM_TOKEN>/setWebhook
```

## Troubleshooting

### API Key Issues

If you encounter errors related to API access:
- Verify that all required API keys are correctly set in the `.env` file
- Check that your API keys are valid and have not expired
- Ensure you have sufficient quota/credits for the APIs you're using

### Docker Issues

If you encounter Docker-related errors:
- Ensure Docker and Docker Compose are correctly installed
- Check if the required ports (8501) are available
- Verify that you have sufficient permissions to run Docker commands

### Python Environment Issues

If you encounter Python-related errors:
- Verify that you're using Python 3.10 or higher
- Ensure all dependencies are correctly installed
- Check if your virtual environment is activated

## Next Steps

After installation, refer to the [User Guide](user_guide.md) for instructions on how to use Open Manus AI and its features.

For more detailed information about the project, see the [Documentation](documentation.md).
