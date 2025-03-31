# Open Manus AI Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [API Reference](#api-reference)
7. [Architecture](#architecture)
8. [Contributing](#contributing)
9. [License](#license)

## Introduction

Open Manus AI is an open-source personal AI assistant with robust conversational abilities, task automation, coding support, and financial analysis. The system is designed to be modular and extensible, allowing for additional plugins and capabilities to be added as needed.

Built on top of GPT-4 and other advanced AI technologies, Open Manus AI provides a comprehensive suite of tools for personal and professional use. The system includes multiple interfaces (Streamlit dashboard, Telegram bot, and CLI) to accommodate different user preferences and use cases.

## Features

### Core Features

- **Advanced Conversational AI**: Powered by GPT-4, Open Manus AI provides natural, context-aware conversations with memory of past interactions.
- **Multi-Agent Collaboration**: The system can delegate tasks to specialized agents for optimal performance.
- **Secure User Memory**: All user data is stored securely and used to personalize interactions.
- **API Integrations**: Connects to various external services for enhanced functionality:
  - Financial data for stock analysis
  - Weather updates
  - News aggregation
  - GitHub integration for code management
  - Render integration for deployment

### Specialized Capabilities

- **Financial Analysis**:
  - Stock data retrieval and visualization
  - Technical analysis with indicators (RSI, MACD, moving averages)
  - Market overview and trends
  - Optional trading capabilities

- **Coding Support**:
  - Code generation in multiple languages
  - Code analysis and optimization
  - GitHub integration for repository management
  - Render integration for deployment

- **Task Automation**:
  - Scheduling and reminders
  - Process automation
  - Data extraction and processing

### User Interfaces

- **Streamlit Dashboard**: Web-based interface with comprehensive visualization and interaction capabilities.
- **Telegram Bot**: Mobile-friendly interface for on-the-go access.
- **Command Line Interface**: For developers and power users who prefer terminal-based interaction.

## Installation

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose (for containerized deployment)
- API keys for external services (OpenAI, financial data, weather, news, GitHub, Render, Telegram)

### Method 1: Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dantiezsaunderson/Open_Manus_AI.git
   cd Open_Manus_AI
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys and configuration
   ```

5. Run the application:
   ```bash
   python -m src.main
   ```

### Method 2: Docker Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dantiezsaunderson/Open_Manus_AI.git
   cd Open_Manus_AI
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys and configuration
   ```

3. Build and run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Access the Streamlit dashboard at http://localhost:8501

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

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

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
MEMORY_STORAGE=file  # Options: file, redis, sqlite
```

### Configuration Files

- **config.yaml**: Main configuration file for application settings
- **logging.yaml**: Logging configuration
- **agents.yaml**: Multi-agent system configuration

## Usage

### Streamlit Dashboard

1. Start the Streamlit dashboard:
   ```bash
   python -m src.interfaces.streamlit_app
   ```
   
2. Open your browser and navigate to http://localhost:8501

3. The dashboard provides access to all features through a user-friendly interface:
   - Conversation tab for chatting with the AI
   - Financial Analysis tab for stock data and market information
   - Coding Support tab for code generation and analysis
   - Weather tab for weather forecasts
   - News tab for latest headlines and articles
   - Settings tab for configuring the application

### Telegram Bot

1. Start the Telegram bot:
   ```bash
   python -m src.interfaces.telegram_bot
   ```

2. Open Telegram and search for your bot (using the bot username)

3. Start a conversation with the bot using the `/start` command

4. Available commands:
   - `/help`: Show help message with all commands
   - `/chat`: Enter chat mode
   - `/finance <symbol>`: Get financial data for a stock
   - `/code <language>`: Generate code
   - `/weather <location>`: Get weather forecast
   - `/news <topic>`: Get latest news
   - `/settings`: View and change settings

### Command Line Interface

1. Start the CLI:
   ```bash
   python -m src.interfaces.cli
   ```

2. Follow the interactive prompts to access different features

3. Type `help` to see all available commands

## API Reference

### Core Modules

#### AI Engine

```python
from src.core.ai_engine import AIEngine

# Initialize the AI engine
ai_engine = AIEngine()

# Generate a response
response = ai_engine.generate_response(prompt, system_message=None)

# Generate embeddings
embedding = ai_engine.generate_embedding(text)
```

#### Memory Manager

```python
from src.core.memory_manager import MemoryManager

# Initialize the memory manager
memory_manager = MemoryManager()

# Save memory
memory_manager.save_memory(user_id, key, value)

# Get memory
value = memory_manager.get_memory(user_id, key, default=None)

# Delete memory
memory_manager.delete_memory(user_id, key=None)
```

### Feature Modules

#### Conversation Module

```python
from src.modules.conversation import ConversationModule

# Initialize the conversation module
conversation = ConversationModule(ai_engine, memory_manager)

# Get a response
response = conversation.get_response(user_id, message)

# Clear conversation history
conversation.clear_history(user_id)
```

#### Financial Analysis Module

```python
from src.modules.financial_analysis import FinancialAnalysisModule

# Initialize the financial analysis module
financial = FinancialAnalysisModule()

# Get stock data
stock_data = financial.get_stock_data(symbol, period="1y")

# Analyze stock
analysis = financial.analyze_stock(symbol)

# Get market overview
market_data = financial.get_market_overview()
```

#### Coding Support Module

```python
from src.modules.coding_support import CodingSupportModule

# Initialize the coding support module
coding = CodingSupportModule(ai_engine)

# Generate code
result = coding.generate_code(prompt, language="python", detailed=True)

# Analyze code
analysis = coding.analyze_code(code, language="python")

# Execute code
output = coding.execute_code(code, timeout=10)
```

### API Integrations

#### OpenAI API

```python
from src.api.openai_api import OpenAIAPI

# Initialize the OpenAI API
openai_api = OpenAIAPI()

# Generate chat completion
response = openai_api.chat_completion(messages, model="gpt-4")

# Generate image
image = openai_api.generate_image(prompt, size="1024x1024")

# Transcribe audio
transcript = openai_api.transcribe_audio(audio_file_path)
```

#### Financial API

```python
from src.api.financial_api import FinancialDataAPI

# Initialize the Financial Data API
financial_api = FinancialDataAPI()

# Get stock data
stock_data = financial_api.get_stock_data(symbol, interval="daily")

# Get company overview
company_data = financial_api.get_company_overview(symbol)

# Get stock quote
quote = financial_api.get_stock_quote(symbol)

# Get company news
news = financial_api.get_company_news(symbol, from_date="2023-01-01")
```

## Architecture

Open Manus AI follows a modular architecture designed for extensibility and maintainability:

```
Open_Manus_AI/
├── src/
│   ├── core/                 # Core components
│   │   ├── ai_engine.py      # AI capabilities
│   │   └── memory_manager.py # User memory management
│   ├── modules/              # Feature modules
│   │   ├── conversation.py   # Conversation handling
│   │   ├── task_automation.py # Task automation
│   │   ├── coding_support.py # Code generation and analysis
│   │   ├── financial_analysis.py # Financial tools
│   │   └── multi_agent.py    # Multi-agent collaboration
│   ├── api/                  # External API integrations
│   │   ├── openai_api.py     # OpenAI integration
│   │   ├── financial_api.py  # Financial data APIs
│   │   ├── weather_api.py    # Weather data
│   │   └── news_api.py       # News services
│   ├── interfaces/           # User interfaces
│   │   ├── streamlit_app.py  # Web dashboard
│   │   ├── telegram_bot.py   # Telegram integration
│   │   └── cli.py            # Command-line interface
│   └── utils/                # Utility functions
│       ├── logger.py         # Logging utilities
│       └── helpers.py        # Helper functions
├── data/                     # Data storage
├── docs/                     # Documentation
├── tests/                    # Unit and integration tests
├── .env.example              # Example environment variables
├── requirements.txt          # Python dependencies
├── setup.py                  # Package installation
├── Dockerfile                # Docker configuration
└── docker-compose.yml        # Docker Compose configuration
```

### Component Interaction

1. **User Interfaces** receive input from users and route it to the appropriate modules
2. **Core Components** provide fundamental capabilities used by all modules
3. **Feature Modules** implement specific functionality domains
4. **API Integrations** connect to external services for enhanced capabilities
5. **Data Storage** persists user data and system state

## Contributing

Contributions to Open Manus AI are welcome! Please follow these steps to contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines for Python code
- Write unit tests for new features
- Update documentation for any changes
- Add comments to explain complex logic

## License

Open Manus AI is released under the MIT License. See the LICENSE file for details.
