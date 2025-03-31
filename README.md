# Open Manus AI Documentation

## Overview

Open Manus AI is an open-source personal AI assistant with advanced features including conversational abilities, multi-agent collaboration, secure user memory, API integrations, and financial analysis capabilities. This documentation provides comprehensive information about the system architecture, features, setup instructions, and usage guidelines.

## Table of Contents

1. [Features](#features)
2. [System Architecture](#system-architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [API Integrations](#api-integrations)
7. [Financial Analysis](#financial-analysis)
8. [Multi-Agent System](#multi-agent-system)
9. [Memory and Personalization](#memory-and-personalization)
10. [Interfaces](#interfaces)
11. [Deployment](#deployment)
12. [Development](#development)
13. [Contributing](#contributing)
14. [License](#license)

## Features

Open Manus AI offers a comprehensive set of features:

- **Advanced Conversational Abilities**: Powered by GPT-4, the system provides natural, context-aware conversations with memory of past interactions.
- **Multi-Agent Collaboration**: Specialized agents work together to handle complex tasks, from research to coding to financial analysis.
- **Secure User Memory**: Personalized interactions with secure storage of user preferences and conversation history.
- **API Integrations**: Connections to financial data, weather, news, and other services.
- **Financial Analysis**: Comprehensive stock analysis, portfolio tracking, and market insights.
- **Code Management**: GitHub integration for version control and code management.
- **Deployment Automation**: Render integration for seamless deployment.
- **Multiple Interfaces**: Access via Streamlit web dashboard or Telegram bot.
- **Docker Support**: Easy deployment with containerization.

## System Architecture

Open Manus AI follows a modular architecture with the following key components:

### Core Components

- **AI Engine**: Manages interactions with OpenAI's GPT-4 API.
- **Memory Manager**: Handles user memory, preferences, and conversation history.
- **Conversation Module**: Manages context-aware conversations and natural language processing.

### Modules

- **Multi-Agent System**: Coordinates specialized agents for different tasks.
- **Financial Analysis**: Processes financial data and generates insights.
- **API Integrations**: Connects to external services and data sources.

### Interfaces

- **Streamlit Dashboard**: Web-based user interface with comprehensive features.
- **Telegram Bot**: Mobile-friendly interface for on-the-go interactions.

### Infrastructure

- **Docker Containers**: Containerized deployment for scalability and portability.
- **GitHub Integration**: Version control and CI/CD pipeline.
- **Render Deployment**: Cloud hosting with automated deployment.

## Installation

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key
- Financial data API keys (optional)
- Telegram Bot token (optional)

### Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dantiezsaunderson/Open_Manus_AI.git
   cd Open_Manus_AI
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. Run the application:
   ```bash
   streamlit run src/main.py
   ```

### Docker Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dantiezsaunderson/Open_Manus_AI.git
   cd Open_Manus_AI
   ```

2. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. Build and run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Access the application at `http://localhost:8501`

## Configuration

Open Manus AI is configured through environment variables in the `.env` file:

### Required Configuration

- `OPENAI_API_KEY`: Your OpenAI API key

### Optional Configuration

- **Financial APIs**:
  - `ALPHA_VANTAGE_API_KEY`: Alpha Vantage API key
  - `FINNHUB_API_KEY`: Finnhub API key
  - `FINANCIALDATA_NET_API_KEY`: FinancialData.net API key

- **Telegram Integration**:
  - `TELEGRAM_BOT_TOKEN`: Telegram Bot token

- **Database Configuration**:
  - `MONGO_USERNAME`: MongoDB username
  - `MONGO_PASSWORD`: MongoDB password

- **Memory Encryption**:
  - `MEMORY_ENCRYPTION_KEY`: Key for encrypting sensitive user data

## Usage

### Streamlit Dashboard

The Streamlit dashboard provides a comprehensive interface with the following sections:

1. **Conversation**: Chat with the AI assistant with context-aware responses.
2. **Financial Dashboard**: Access financial analysis tools, stock information, and portfolio tracking.
3. **Multi-Agent System**: Submit tasks to specialized agents and monitor their progress.
4. **Settings**: Configure user preferences, API keys, and system settings.

### Telegram Bot

The Telegram bot offers a mobile-friendly interface with commands for:

- General conversation
- Financial analysis and stock information
- Portfolio and watchlist management
- Task submission to the multi-agent system
- User preference management

#### Telegram Commands

- `/start` - Start or restart the bot
- `/help` - Show help message
- `/settings` - Manage preferences
- `/finance` - Financial dashboard
- `/stock [symbol]` - Get stock information
- `/analyze` - Analyze a stock
- `/portfolio` - View portfolio
- `/watchlist` - View watchlist
- `/market` - Get market overview
- `/task [description]` - Submit a task
- `/agents` - View active agents

## API Integrations

Open Manus AI integrates with several external APIs to provide enhanced functionality:

### Financial Data APIs

1. **FinancialData.net API**
   - Stock symbols and prices
   - Financial statements (income statements, balance sheets, cash flows)
   - Financial ratios and insider trading data

2. **Yahoo Finance API**
   - Comprehensive stock market data with charts
   - Insider trading information
   - Technical indicators and company metrics
   - SEC filings and analyst opinions

3. **Alpha Vantage API**
   - Real-time and historical stock data
   - Technical indicators
   - Forex and cryptocurrency data

4. **Finnhub API**
   - Real-time market data
   - Company financials
   - News and sentiment analysis

### OpenAI API

- GPT-4 for natural language processing and generation
- Context-aware conversations
- Code generation and analysis

## Financial Analysis

The financial analysis module provides comprehensive tools for stock analysis and portfolio management:

### Stock Analysis

- **Price Data**: Historical and real-time price information
- **Technical Indicators**: Moving averages, RSI, MACD, Bollinger Bands
- **Fundamental Analysis**: Financial statements, ratios, and metrics
- **Visualization**: Interactive charts with technical indicators

### Portfolio Management

- **Portfolio Tracking**: Monitor holdings, performance, and allocation
- **Watchlist**: Track stocks of interest
- **Performance Analysis**: Gain/loss calculations and comparisons
- **Risk Assessment**: Volatility and diversification metrics

### Market Insights

- **Market Overview**: Major indices and market trends
- **Sector Analysis**: Performance by sector
- **News Integration**: Relevant financial news and events
- **Analyst Opinions**: Recommendations and price targets

## Multi-Agent System

The enhanced multi-agent system coordinates specialized agents to handle complex tasks:

### Agent Types

1. **Research Agent**: Gathers information and conducts research
2. **Coding Agent**: Generates and analyzes code
3. **Financial Agents**:
   - **Stock Screener Agent**: Filters stocks based on criteria
   - **Technical Analysis Agent**: Performs technical analysis
   - **Fundamental Analysis Agent**: Analyzes financial statements

### Task Delegation

The system automatically delegates tasks to the most appropriate agent based on:
- Task type and requirements
- Agent specialization and capabilities
- Current agent workload

### Collaboration

Agents can collaborate on complex tasks by:
- Sharing information and intermediate results
- Requesting assistance from other agents
- Combining outputs for comprehensive results

## Memory and Personalization

The enhanced memory system provides secure storage and retrieval of user information:

### User Memory

- **Conversation History**: Past interactions and context
- **User Preferences**: Communication style, detail level, topics of interest
- **Personal Information**: User-provided facts and details

### Memory Features

- **Secure Storage**: Encrypted storage of sensitive information
- **Context-Aware Retrieval**: Relevant information based on conversation context
- **Memory Summarization**: Condensed information for efficient retrieval
- **Multi-User Support**: Isolated memory spaces for different users

### Personalization

- **Adaptive Responses**: Tailored to user preferences and history
- **Topic Tracking**: Awareness of topics discussed in current and past conversations
- **Preference Learning**: Gradual adaptation to user preferences and behavior

## Interfaces

### Streamlit Dashboard

The enhanced Streamlit dashboard provides a comprehensive web interface with:

- **Improved UI/UX**: Clean, intuitive design with responsive layout
- **Conversation Interface**: Natural chat experience with context awareness
- **Financial Dashboard**: Comprehensive financial analysis tools
- **Multi-Agent Interface**: Task submission and monitoring
- **Settings Management**: User preferences and API configuration

### Telegram Bot

The Telegram integration offers a mobile-friendly interface with:

- **Conversational Interface**: Natural language interaction
- **Command System**: Structured commands for specific functions
- **Interactive Elements**: Buttons and menus for easier navigation
- **Rich Media Support**: Charts, images, and formatted text
- **Notification System**: Updates on task completion and important events

## Deployment

### Docker Deployment

Open Manus AI uses Docker for containerized deployment with the following services:

1. **Main Application**: Streamlit dashboard and core functionality
2. **Telegram Bot**: Separate service for Telegram integration
3. **MongoDB**: Database for persistent storage
4. **Redis**: Caching and message queuing

The `docker-compose.yml` file configures these services with appropriate networking and volume management.

### Render Deployment

The application is deployed to Render with automated CI/CD:

1. GitHub Actions workflow tests and builds the application
2. On successful build, the application is deployed to Render
3. The deployment is verified and monitored

Access the deployed application at: https://open-manus-ai.onrender.com/

## Development

### Project Structure

```
Open_Manus_AI/
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── data/
├── logs/
├── src/
│   ├── api/
│   │   ├── financialdata_net_api.py
│   │   ├── yahoo_finance_api.py
│   │   └── financial_api.py
│   ├── core/
│   │   ├── ai_engine.py
│   │   ├── enhanced_memory_manager.py
│   │   └── memory_manager.py
│   ├── integrations/
│   │   └── enhanced_telegram_integration.py
│   ├── modules/
│   │   ├── enhanced_conversation.py
│   │   ├── enhanced_financial_analysis.py
│   │   ├── enhanced_multi_agent.py
│   │   ├── financial_analysis.py
│   │   └── multi_agent.py
│   ├── ui/
│   │   └── enhanced_streamlit_dashboard.py
│   ├── main.py
│   └── telegram_bot.py
├── tests/
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.telegram
├── requirements.txt
└── README.md
```

### Development Workflow

1. **Fork and Clone**: Fork the repository and clone it locally
2. **Branch**: Create a feature branch for your changes
3. **Develop**: Make changes and add tests
4. **Test**: Run tests to ensure functionality
5. **Commit**: Commit changes with descriptive messages
6. **Push**: Push changes to your fork
7. **Pull Request**: Create a pull request to the main repository

### Testing

Run tests with pytest:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=src tests/
```

### CI/CD Pipeline

The GitHub Actions workflow automates:

1. **Testing**: Running pytest and flake8
2. **Building**: Building Docker images
3. **Deployment**: Deploying to Render (for main branch or manual trigger)

## Contributing

Contributions to Open Manus AI are welcome! Please follow these guidelines:

1. Check existing issues or create a new one to discuss your proposed changes
2. Follow the development workflow described above
3. Ensure your code passes all tests and linting
4. Update documentation for any new features or changes
5. Submit a pull request with a clear description of your changes

## License

Open Manus AI is released under the MIT License. See the LICENSE file for details.

---

## Contact

For questions or support, please open an issue on the GitHub repository or contact the maintainers directly.

Repository: https://github.com/dantiezsaunderson/Open_Manus_AI
Deployed Application: https://open-manus-ai.onrender.com/
