# User Guide

## Getting Started

Welcome to Open Manus AI! This guide will help you get started with using the various features and interfaces of the system.

## Accessing Open Manus AI

Open Manus AI provides three different interfaces to accommodate different user preferences:

1. **Streamlit Dashboard**: A web-based interface with comprehensive visualization and interaction capabilities
2. **Telegram Bot**: A mobile-friendly interface for on-the-go access
3. **Command Line Interface**: For developers and power users who prefer terminal-based interaction

### Streamlit Dashboard

The Streamlit dashboard is the most feature-rich interface for Open Manus AI. To access it:

1. Ensure the application is running (see [Installation Guide](installation.md))
2. Open your web browser and navigate to http://localhost:8501
3. You'll see the main dashboard with multiple tabs for different features

#### Dashboard Navigation

The dashboard includes the following tabs:

- **Conversation**: Chat with the AI assistant
- **Financial Analysis**: Analyze stocks and market data
- **Coding Support**: Generate and analyze code
- **Weather**: Get weather forecasts
- **News**: Browse and search news articles
- **Settings**: Configure the application

### Telegram Bot

The Telegram bot provides a convenient way to access Open Manus AI from your mobile device:

1. Ensure the Telegram bot is running (see [Installation Guide](installation.md))
2. Open Telegram and search for your bot (using the bot username)
3. Start a conversation with the bot using the `/start` command

#### Telegram Commands

The bot supports the following commands:

- `/start`: Start the bot and see main menu
- `/help`: Show help message with all commands
- `/chat`: Enter chat mode
- `/reset`: Reset conversation history
- `/finance <symbol>`: Get financial data for a stock
- `/code <language>`: Generate code
- `/weather <location>`: Get weather forecast
- `/news <topic>`: Get latest news
- `/analyze_code`: Analyze code
- `/analyze_stock <symbol>`: Get detailed stock analysis
- `/market`: Get market overview
- `/settings`: View and change settings
- `/feedback`: Send feedback about the bot

### Command Line Interface

The CLI provides a text-based interface for power users:

1. Ensure the application is installed (see [Installation Guide](installation.md))
2. Open a terminal and navigate to the project directory
3. Run the CLI: `python -m src.interfaces.cli`
4. Follow the interactive prompts to access different features

## Core Features

### Conversational AI

Open Manus AI provides natural, context-aware conversations:

1. Navigate to the Conversation tab in the dashboard or use the Telegram bot
2. Type your message in the input field and send it
3. The AI will respond based on the context of your conversation
4. The system remembers previous messages, allowing for contextual follow-ups

Tips:
- Use clear, specific language for best results
- You can ask follow-up questions without repeating context
- To reset the conversation, click "Clear History" or use `/reset` in Telegram

### Financial Analysis

The financial analysis features help you analyze stocks and market data:

1. Navigate to the Financial Analysis tab in the dashboard or use `/finance` in Telegram
2. Enter a stock symbol (e.g., AAPL for Apple)
3. View stock data, charts, and analysis

Available features:
- Stock price data and charts
- Technical indicators (RSI, MACD, moving averages)
- Company information
- Market overview

### Coding Support

The coding support features help you generate and analyze code:

1. Navigate to the Coding Support tab in the dashboard or use `/code` in Telegram
2. Select the programming language
3. Describe what you want to create
4. View the generated code and explanation

Available features:
- Code generation in multiple languages
- Code analysis and optimization
- Code execution (in sandbox environment)

### Weather Information

Get weather forecasts for any location:

1. Navigate to the Weather tab in the dashboard or use `/weather` in Telegram
2. Enter a location (city name or coordinates)
3. View current weather and forecast

Available features:
- Current weather conditions
- 5-day forecast
- Air quality information

### News Updates

Stay updated with the latest news:

1. Navigate to the News tab in the dashboard or use `/news` in Telegram
2. Browse top headlines or search for specific topics
3. View article summaries and links to full articles

Available features:
- Top headlines by category
- News search
- Article summarization

## Advanced Features

### Multi-Agent Collaboration

Open Manus AI uses a multi-agent system to handle complex tasks:

1. The system automatically delegates tasks to specialized agents
2. Each agent has expertise in a specific domain
3. Agents collaborate to provide comprehensive responses

This happens automatically in the background, but you can see it in action when asking complex questions that span multiple domains.

### User Memory

The system maintains a secure memory of your interactions:

1. Your conversation history is stored securely
2. Preferences and settings are remembered
3. The system uses this information to personalize responses

To manage your stored data:
- Use the Settings tab in the dashboard
- Use `/settings` in Telegram
- Use the "clear" command in the CLI

## Tips and Best Practices

1. **Be Specific**: The more specific your requests, the better the results
2. **Use Natural Language**: You can communicate with the AI in natural, conversational language
3. **Provide Context**: When necessary, provide relevant context for your questions
4. **Explore Features**: Try different features and interfaces to find what works best for you
5. **Feedback**: Use the feedback feature to report issues or suggest improvements

## Troubleshooting

If you encounter issues:

1. Check that all required API keys are correctly configured
2. Verify that the application is running correctly
3. Consult the [Installation Guide](installation.md) for setup issues
4. Check the logs for error messages
5. Report persistent issues through the feedback feature or on GitHub

## Next Steps

Now that you're familiar with Open Manus AI, you might want to:

1. Explore the [API Reference](documentation.md#api-reference) if you're a developer
2. Learn about the [Architecture](documentation.md#architecture) to understand how the system works
3. Consider [Contributing](documentation.md#contributing) to the project
