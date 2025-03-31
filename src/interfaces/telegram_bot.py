"""
Telegram Bot Integration Module

This module implements a Telegram bot interface for the Open Manus AI system.
"""

import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import Open Manus AI modules
from src.core.ai_engine import AIEngine
from src.core.memory_manager import MemoryManager
from src.modules.conversation import ConversationModule
from src.modules.task_automation import TaskAutomationModule
from src.modules.coding_support import CodingSupportModule
from src.modules.financial_analysis import FinancialAnalysisModule
from src.modules.multi_agent import MultiAgentSystem
from src.api.openai_api import OpenAIAPI
from src.api.financial_api import FinancialDataAPI
from src.api.weather_api import WeatherAPI
from src.api.news_api import NewsAPI

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class TelegramBot:
    """
    Telegram Bot interface for Open Manus AI.
    """
    
    def __init__(self):
        """Initialize the Telegram Bot interface."""
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        if not self.token:
            logger.error("Telegram bot token not found in environment variables")
            raise ValueError("Telegram bot token not found")
        
        # Initialize components
        self.memory_manager = MemoryManager()
        self.ai_engine = AIEngine()
        self.conversation_module = ConversationModule(self.ai_engine, self.memory_manager)
        self.task_automation = TaskAutomationModule(self.ai_engine, self.memory_manager)
        self.coding_support = CodingSupportModule(self.ai_engine)
        self.financial_analysis = FinancialAnalysisModule()
        self.multi_agent_system = MultiAgentSystem(self.ai_engine)
        
        # Initialize API integrations
        self.openai_api = OpenAIAPI()
        self.financial_api = FinancialDataAPI()
        self.weather_api = WeatherAPI()
        self.news_api = NewsAPI()
        
        # User states
        self.user_states = {}
        
        logger.info("Telegram Bot interface initialized")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command."""
        user = update.effective_user
        user_id = str(user.id)
        
        # Store user info in memory
        self.memory_manager.save_memory(user_id, "name", user.first_name)
        self.memory_manager.save_memory(user_id, "username", user.username)
        
        # Welcome message
        welcome_message = (
            f"👋 Hello, {user.first_name}! I'm Open Manus AI, your personal AI assistant.\n\n"
            "I can help you with:\n"
            "• 💬 Conversations and questions\n"
            "• 📈 Financial analysis\n"
            "• 💻 Coding support\n"
            "• 🌤️ Weather information\n"
            "• 📰 News updates\n\n"
            "Use /help to see all available commands."
        )
        
        # Create keyboard with main features
        keyboard = [
            [
                InlineKeyboardButton("💬 Chat", callback_data="mode_chat"),
                InlineKeyboardButton("📈 Finance", callback_data="mode_finance")
            ],
            [
                InlineKeyboardButton("💻 Code", callback_data="mode_code"),
                InlineKeyboardButton("🌤️ Weather", callback_data="mode_weather"),
                InlineKeyboardButton("📰 News", callback_data="mode_news")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command."""
        help_text = (
            "🤖 *Open Manus AI Commands*\n\n"
            "*Basic Commands:*\n"
            "/start - Start the bot and see main menu\n"
            "/help - Show this help message\n"
            "/chat - Enter chat mode\n"
            "/reset - Reset conversation history\n\n"
            
            "*Feature Commands:*\n"
            "/finance <symbol> - Get financial data for a stock\n"
            "/code <language> - Generate code (follow with your description)\n"
            "/weather <location> - Get weather forecast\n"
            "/news <topic> - Get latest news\n\n"
            
            "*Advanced Commands:*\n"
            "/analyze_code - Analyze code (send code after this command)\n"
            "/analyze_stock <symbol> - Get detailed stock analysis\n"
            "/market - Get market overview\n"
            "/task <description> - Create a task\n\n"
            
            "*Settings:*\n"
            "/settings - View and change settings\n"
            "/feedback - Send feedback about the bot\n"
        )
        
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /chat command."""
        user_id = str(update.effective_user.id)
        self.user_states[user_id] = "chat"
        
        await update.message.reply_text(
            "💬 I'm in chat mode now. You can ask me anything or have a conversation. "
            "Your messages will be processed using my AI capabilities."
        )
    
    async def reset_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /reset command."""
        user_id = str(update.effective_user.id)
        
        # Clear conversation history
        self.conversation_module.clear_history(user_id)
        
        await update.message.reply_text(
            "🔄 Your conversation history has been reset. We're starting fresh!"
        )
    
    async def finance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /finance command."""
        user_id = str(update.effective_user.id)
        
        # Check if a stock symbol was provided
        if context.args:
            symbol = context.args[0].upper()
            
            await update.message.reply_text(f"📊 Fetching financial data for {symbol}...")
            
            # Get stock data
            stock_data = self.financial_analysis.get_stock_data(symbol)
            
            if stock_data.get('success', False):
                # Format the response
                company_name = stock_data.get('company_name', symbol)
                sector = stock_data.get('sector', 'Unknown')
                market_cap = stock_data.get('market_cap', 'Unknown')
                
                # Get the latest price and change
                stats = stock_data.get('stats', {})
                latest_price = stats.get('latest_price', 0)
                price_change = stats.get('price_change', 0)
                price_change_pct = stats.get('price_change_pct', 0)
                
                # Create the response message
                response = (
                    f"📈 *{company_name} ({symbol})*\n\n"
                    f"*Price:* ${latest_price:.2f}\n"
                    f"*Change:* {price_change:.2f} ({price_change_pct:.2f}%)\n"
                    f"*Sector:* {sector}\n"
                    f"*Market Cap:* {market_cap}\n\n"
                )
                
                # Add buttons for more actions
                keyboard = [
                    [
                        InlineKeyboardButton("📊 Analyze", callback_data=f"analyze_stock_{symbol}"),
                        InlineKeyboardButton("📰 News", callback_data=f"stock_news_{symbol}")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")
            else:
                await update.message.reply_text(
                    f"❌ Error retrieving data for {symbol}: {stock_data.get('error', 'Unknown error')}"
                )
        else:
            # No symbol provided, show instructions
            await update.message.reply_text(
                "📈 *Financial Analysis*\n\n"
                "Please provide a stock symbol to get financial data.\n"
                "Example: `/finance AAPL`\n\n"
                "Or use one of these options:",
                parse_mode="Markdown"
            )
            
            # Show buttons for common actions
            keyboard = [
                [
                    InlineKeyboardButton("Market Overview", callback_data="market_overview"),
                    InlineKeyboardButton("Top Stocks", callback_data="top_stocks")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text("Choose an option:", reply_markup=reply_markup)
    
    async def code_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /code command."""
        user_id = str(update.effective_user.id)
        
        # Check if language was provided
        if context.args:
            # First argument is the language, rest is the prompt
            language = context.args[0].lower()
            prompt = " ".join(context.args[1:])
            
            # If no prompt in command, set state to wait for prompt
            if not prompt:
                self.user_states[user_id] = f"code_{language}"
                await update.message.reply_text(
                    f"💻 I'll generate {language} code for you. Please describe what you want me to create."
                )
                return
            
            # Generate code
            await self._generate_code(update, language, prompt)
        else:
            # No language provided, show options
            keyboard = [
                [
                    InlineKeyboardButton("Python", callback_data="code_python"),
                    InlineKeyboardButton("JavaScript", callback_data="code_javascript"),
                    InlineKeyboardButton("Java", callback_data="code_java")
                ],
                [
                    InlineKeyboardButton("C++", callback_data="code_cpp"),
                    InlineKeyboardButton("HTML/CSS", callback_data="code_html"),
                    InlineKeyboardButton("SQL", callback_data="code_sql")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "💻 *Code Generation*\n\n"
                "Please select a programming language:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    
    async def _generate_code(self, update, language, prompt):
        """Generate code based on prompt and language."""
        await update.message.reply_text(f"💻 Generating {language} code for: {prompt}")
        
        # Generate code
        result = self.coding_support.generate_code(prompt, language)
        
        if result.get('success', False):
            code = result.get('code', '')
            
            # Send code with proper formatting
            await update.message.reply_text(f"```{language}\n{code}\n```", parse_mode="Markdown")
            
            # Send explanation if it's not too long
            explanation = result.get('explanation', '')
            if len(explanation) > 4000:
                explanation = explanation[:4000] + "...\n\n(Explanation truncated due to length)"
            
            await update.message.reply_text(explanation)
        else:
            await update.message.reply_text(
                f"❌ Error generating code: {result.get('explanation', 'Unknown error')}"
            )
    
    async def analyze_code_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /analyze_code command."""
        user_id = str(update.effective_user.id)
        self.user_states[user_id] = "analyze_code"
        
        # Ask for the code and language
        keyboard = [
            [
                InlineKeyboardButton("Python", callback_data="analyze_python"),
                InlineKeyboardButton("JavaScript", callback_data="analyze_javascript"),
                InlineKeyboardButton("Java", callback_data="analyze_java")
            ],
            [
                InlineKeyboardButton("C++", callback_data="analyze_cpp"),
                InlineKeyboardButton("HTML/CSS", callback_data="analyze_html"),
                InlineKeyboardButton("SQL", callback_data="analyze_sql")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "💻 *Code Analysis*\n\n"
            "Please select the programming language of the code you want to analyze:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def weather_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /weather command."""
        # Check if location was provided
        if context.args:
            location = " ".join(context.args)
            await self._get_weather(update, location)
        else:
            user_id = str(update.effective_user.id)
            self.user_states[user_id] = "weather"
            
            await update.message.reply_text(
                "🌤️ Please provide a location (city name or coordinates) to get the weather forecast."
            )
    
    async def _get_weather(self, update, location):
        """Get weather for a location."""
        await update.message.reply_text(f"🌤️ Fetching weather for {location}...")
        
        # Get current weather
        weather_data = self.weather_api.get_current_weather(location)
        
        if weather_data.get('success', False):
            data = weather_data.get('weather_data', {})
            
            # Extract location info
            location_name = data.get('location', {}).get('name', location)
            country = data.get('location', {}).get('country', '')
            
            # Extract weather info
            weather = data.get('weather', {})
            temp = weather.get('temperature', {}).get('current', 0)
            feels_like = weather.get('temperature', {}).get('feels_like', 0)
            condition = weather.get('condition', '')
            description = weather.get('description', '')
            humidity = weather.get('humidity', 0)
            wind_speed = weather.get('wind', {}).get('speed', 0)
            
            # Format response
            units = data.get('units', 'metric')
            temp_unit = "°C" if units == "metric" else "°F"
            speed_unit = "m/s" if units == "metric" else "mph"
            
            response = (
                f"🌤️ *Weather in {location_name}, {country}*\n\n"
                f"*Temperature:* {temp}{temp_unit} (Feels like: {feels_like}{temp_unit})\n"
                f"*Condition:* {condition} - {description}\n"
                f"*Humidity:* {humidity}%\n"
                f"*Wind:* {wind_speed} {speed_unit}\n"
            )
            
            # Add buttons for more info
            keyboard = [
                [
                    InlineKeyboardButton("5-Day Forecast", callback_data=f"forecast_{location}"),
                    InlineKeyboardButton("Air Quality", callback_data=f"air_quality_{location}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await update.message.reply_text(
                f"❌ Error getting weather for {location}: {weather_data.get('error', 'Unknown error')}"
            )
    
    async def news_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /news command."""
        # Check if topic was provided
        if context.args:
            query = " ".join(context.args)
            await self._get_news(update, query)
        else:
            # Show news categories
            keyboard = [
                [
                    InlineKeyboardButton("Top Headlines", callback_data="news_headlines"),
                    InlineKeyboardButton("Business", callback_data="news_business")
                ],
                [
                    InlineKeyboardButton("Technology", callback_data="news_technology"),
                    InlineKeyboardButton("Science", callback_data="news_science")
                ],
                [
                    InlineKeyboardButton("Health", callback_data="news_health"),
                    InlineKeyboardButton("Sports", callback_data="news_sports")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "📰 *News*\n\n"
                "Please select a news category or use `/news <topic>` to search for specific news.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    
    async def _get_news(self, update, query):
        """Get news for a topic."""
        await update.message.reply_text(f"📰 Searching news about: {query}")
        
        # Search news
        news_data = self.news_api.search_news(query=query, page_size=5)
        
        if news_data.get('success', False):
            articles = news_data.get('articles', [])
            
            if articles:
                # Send each article
                for i, article in enumerate(articles[:5]):
                    title = article.get('title', '')
                    source = article.get('source', {}).get('name', '')
                    description = article.get('description', '')
                    url = article.get('url', '')
                    
                    response = (
                        f"📰 *{title}*\n"
                        f"Source: {source}\n\n"
                        f"{description}\n\n"
                        f"[Read more]({url})"
                    )
                    
                    await update.message.reply_text(response, parse_mode="Markdown")
                    
                    # Add a small delay between messages
                    if i < len(articles) - 1:
                        await asyncio.sleep(0.5)
                
                # Add button to summarize
                keyboard = [
                    [InlineKeyboardButton("Summarize Articles", callback_data=f"summarize_{query}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "Would you like me to summarize these articles?",
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(f"No news found for: {query}")
        else:
            await update.message.reply_text(
                f"❌ Error searching news: {news_data.get('error', 'Unknown error')}"
            )
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /settings command."""
        user_id = str(update.effective_user.id)
        
        # Get user preferences
        preferences = self.memory_manager.get_memory(user_id, "preferences", {})
        
        # Format current settings
        settings_text = (
            "⚙️ *Your Settings*\n\n"
            f"*Language:* {preferences.get('language', 'English')}\n"
            f"*Units:* {preferences.get('units', 'Metric')}\n"
            f"*News Country:* {preferences.get('news_country', 'US')}\n"
        )
        
        # Create settings buttons
        keyboard = [
            [
                InlineKeyboardButton("Change Language", callback_data="settings_language"),
                InlineKeyboardButton("Change Units", callback_data="settings_units")
            ],
            [
                InlineKeyboardButton("Change News Country", callback_data="settings_news_country"),
                InlineKeyboardButton("Reset All Settings", callback_data="settings_reset")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(settings_text, reply_markup=reply_markup, parse_mode="Markdown")
    
    async def feedback_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /feedback command."""
        user_id = str(update.effective_user.id)
        self.user_states[user_id] = "feedback"
        
        await update.message.reply_text(
            "📝 I'd love to hear your feedback! Please share your thoughts, suggestions, or report any issues."
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages."""
        if not update.message or not update.message.text:
            return
        
        user_id = str(update.effective_user.id)
        message_text = update.message.text
        
        # Check user state
        state = self.user_states.get(user_id, "chat")
        
        if state.startswith("code_"):
            # Generate code in the specified language
            language = state.split("_")[1]
            await self._generate_code(update, language, message_text)
            self.user_states[user_id] = "chat"  # Reset state
        
        elif state == "analyze_code":
            # User needs to select language first
            await update.message.reply_text(
                "Please select the programming language using the buttons above."
            )
        
        elif state.startswith("analyze_"):
            # Analyze code in the specified language
            language = state.split("_")[1]
            
            await update.message.reply_text(f"💻 Analyzing {language} code...")
            
            # Analyze code
            result = self.coding_support.analyze_code(message_text, language)
            
            if result.get('success', False):
                analysis = result.get('analysis', '')
                
                # Split long analysis into multiple messages if needed
                if len(analysis) > 4000:
                    chunks = [analysis[i:i+4000] for i in range(0, len(analysis), 4000)]
                    for chunk in chunks:
                        await update.message.reply_text(chunk)
                else:
                    await update.message.reply_text(analysis)
            else:
                await update.message.reply_text(
                    f"❌ Error analyzing code: {result.get('analysis', 'Unknown error')}"
                )
            
            self.user_states[user_id] = "chat"  # Reset state
        
        elif state == "weather":
            # Get weather for the provided location
            await self._get_weather(update, message_text)
            self.user_states[user_id] = "chat"  # Reset state
        
        elif state == "feedback":
            # Save feedback
            self.memory_manager.save_memory(user_id, "feedback", message_text)
            
            await update.message.reply_text(
                "🙏 Thank you for your feedback! We appreciate your input and will use it to improve Open Manus AI."
            )
            
            self.user_states[user_id] = "chat"  # Reset state
        
        else:  # Default to chat mode
            # Get response from conversation module
            with update.message.chat.action("typing"):
                response = self.conversation_module.get_response(user_id, message_text)
            
            await update.message.reply_text(response)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards."""
        query = update.callback_query
        user_id = str(query.from_user.id)
        data = query.data
        
        # Acknowledge the callback
        await query.answer()
        
        # Handle different callback types
        if data.startswith("mode_"):
            # Mode selection
            mode = data.split("_")[1]
            
            if mode == "chat":
                self.user_states[user_id] = "chat"
                await query.message.reply_text("💬 I'm in chat mode. How can I help you today?")
            
            elif mode == "finance":
                await query.message.reply_text(
                    "📈 *Financial Analysis*\n\n"
                    "Please use `/finance <symbol>` to get data for a specific stock.\n"
                    "Example: `/finance AAPL`",
                    parse_mode="Markdown"
                )
            
            elif mode == "code":
                await self.code_command(update, context)
            
            elif mode == "weather":
                await query.message.reply_text(
                    "🌤️ *Weather*\n\n"
                    "Please use `/weather <location>` to get the forecast.\n"
                    "Example: `/weather New York`",
                    parse_mode="Markdown"
                )
            
            elif mode == "news":
                await self.news_command(update, context)
        
        elif data.startswith("code_"):
            # Code language selection
            language = data.split("_")[1]
            self.user_states[user_id] = f"code_{language}"
            
            await query.message.reply_text(
                f"💻 I'll generate {language} code for you. Please describe what you want me to create."
            )
        
        elif data.startswith("analyze_"):
            # Code analysis language selection
            language = data.split("_")[1]
            self.user_states[user_id] = f"analyze_{language}"
            
            await query.message.reply_text(
                f"💻 Please send me the {language} code you want to analyze."
            )
        
        elif data.startswith("analyze_stock_"):
            # Stock analysis
            symbol = data.split("_")[2]
            
            await query.message.reply_text(f"📊 Analyzing {symbol}...")
            
            # Get stock analysis
            analysis = self.financial_analysis.analyze_stock(symbol)
            
            if analysis.get('success', False):
                # Format the response
                company_info = analysis.get('company_info', {})
                company_name = company_info.get('company_name', symbol)
                
                # Technical indicators
                indicators = analysis.get('technical_indicators', {})
                
                # Create response
                response = (
                    f"📊 *Analysis for {company_name} ({symbol})*\n\n"
                    f"*Price:* ${indicators.get('price', 0):.2f}\n"
                    f"*RSI:* {indicators.get('rsi', 0):.2f}\n"
                    f"*MACD:* {indicators.get('macd', 0):.2f}\n\n"
                    "*Signals:*\n"
                )
                
                # Add signals
                if indicators.get('above_ma20', False):
                    response += "✅ Price above 20-day moving average\n"
                else:
                    response += "❌ Price below 20-day moving average\n"
                    
                if indicators.get('above_ma50', False):
                    response += "✅ Price above 50-day moving average\n"
                else:
                    response += "❌ Price below 50-day moving average\n"
                    
                if indicators.get('rsi_oversold', False):
                    response += "⚠️ RSI indicates oversold conditions\n"
                elif indicators.get('rsi_overbought', False):
                    response += "⚠️ RSI indicates overbought conditions\n"
                else:
                    response += "✅ RSI in neutral range\n"
                    
                if indicators.get('macd_bullish', False):
                    response += "✅ MACD indicates bullish trend\n"
                else:
                    response += "❌ MACD indicates bearish trend\n"
                
                await query.message.reply_text(response, parse_mode="Markdown")
            else:
                await query.message.reply_text(
                    f"❌ Error analyzing {symbol}: {analysis.get('error', 'Unknown error')}"
                )
        
        elif data == "market_overview":
            # Market overview
            await query.message.reply_text("📊 Fetching market overview...")
            
            # Get market data
            market_data = self.financial_analysis.get_market_overview()
            
            if market_data.get('success', False):
                market_indices = market_data.get('data', {})
                
                if market_indices:
                    # Create response
                    response = "📊 *Market Overview*\n\n"
                    
                    for symbol, data in market_indices.items():
                        name = data.get('name', symbol)
                        price = data.get('latest_price', 0)
                        change = data.get('change', 0)
                        change_pct = data.get('change_pct', 0)
                        
                        # Add emoji based on change
                        emoji = "🟢" if change >= 0 else "🔴"
                        
                        response += f"{emoji} *{name}*: ${price:.2f} ({change_pct:.2f}%)\n"
                    
                    await query.message.reply_text(response, parse_mode="Markdown")
                else:
                    await query.message.reply_text("No market data available.")
            else:
                await query.message.reply_text(
                    f"❌ Error getting market overview: {market_data.get('error', 'Unknown error')}"
                )
        
        elif data.startswith("forecast_"):
            # Weather forecast
            location = data.split("_", 1)[1]
            
            await query.message.reply_text(f"🌤️ Fetching forecast for {location}...")
            
            # Get forecast
            forecast = self.weather_api.get_weather_forecast(location)
            
            if forecast.get('success', False):
                forecast_data = forecast.get('forecast_data', {})
                forecast_days = forecast_data.get('forecast', {})
                
                if forecast_days:
                    # Create response
                    response = f"🌤️ *5-Day Forecast for {location}*\n\n"
                    
                    for date, day_data in list(forecast_days.items())[:5]:
                        # Format date
                        date_obj = datetime.strptime(date, "%Y-%m-%d")
                        day_str = date_obj.strftime("%a, %b %d")
                        
                        # Get mid-day forecast
                        mid_day = None
                        for item in day_data:
                            item_time = datetime.fromisoformat(item['datetime'])
                            if 11 <= item_time.hour <= 14:
                                mid_day = item
                                break
                        
                        if not mid_day and day_data:
                            mid_day = day_data[len(day_data)//2]
                        
                        if mid_day:
                            # Get weather info
                            temp = mid_day.get('temperature', {}).get('current', 0)
                            condition = mid_day.get('weather', {}).get('condition', '')
                            pop = mid_day.get('precipitation', {}).get('probability', 0) * 100
                            
                            # Add emoji based on condition
                            emoji = "☀️"
                            if "rain" in condition.lower():
                                emoji = "🌧️"
                            elif "cloud" in condition.lower():
                                emoji = "☁️"
                            elif "snow" in condition.lower():
                                emoji = "❄️"
                            elif "storm" in condition.lower() or "thunder" in condition.lower():
                                emoji = "⛈️"
                            
                            # Add to response
                            units = forecast_data.get('units', 'metric')
                            temp_unit = "°C" if units == "metric" else "°F"
                            
                            response += f"{emoji} *{day_str}*: {temp}{temp_unit}, {condition}, Rain: {pop:.0f}%\n\n"
                    
                    await query.message.reply_text(response, parse_mode="Markdown")
                else:
                    await query.message.reply_text("No forecast data available.")
            else:
                await query.message.reply_text(
                    f"❌ Error getting forecast: {forecast.get('error', 'Unknown error')}"
                )
        
        elif data.startswith("news_"):
            # News category
            category = data.split("_")[1]
            
            if category == "headlines":
                # Get top headlines
                await query.message.reply_text("📰 Fetching top headlines...")
                
                headlines = self.news_api.get_top_headlines(page_size=5)
                
                if headlines.get('success', False):
                    articles = headlines.get('headlines', [])
                    
                    if articles:
                        for article in articles[:5]:
                            title = article.get('title', '')
                            source = article.get('source', {}).get('name', '')
                            description = article.get('description', '')
                            url = article.get('url', '')
                            
                            response = (
                                f"📰 *{title}*\n"
                                f"Source: {source}\n\n"
                                f"{description}\n\n"
                                f"[Read more]({url})"
                            )
                            
                            await query.message.reply_text(response, parse_mode="Markdown")
                            await asyncio.sleep(0.5)
                    else:
                        await query.message.reply_text("No headlines found.")
                else:
                    await query.message.reply_text(
                        f"❌ Error getting headlines: {headlines.get('error', 'Unknown error')}"
                    )
            else:
                # Get category news
                await query.message.reply_text(f"📰 Fetching {category} news...")
                
                headlines = self.news_api.get_top_headlines(category=category, page_size=5)
                
                if headlines.get('success', False):
                    articles = headlines.get('headlines', [])
                    
                    if articles:
                        for article in articles[:5]:
                            title = article.get('title', '')
                            source = article.get('source', {}).get('name', '')
                            description = article.get('description', '')
                            url = article.get('url', '')
                            
                            response = (
                                f"📰 *{title}*\n"
                                f"Source: {source}\n\n"
                                f"{description}\n\n"
                                f"[Read more]({url})"
                            )
                            
                            await query.message.reply_text(response, parse_mode="Markdown")
                            await asyncio.sleep(0.5)
                    else:
                        await query.message.reply_text(f"No {category} news found.")
                else:
                    await query.message.reply_text(
                        f"❌ Error getting {category} news: {headlines.get('error', 'Unknown error')}"
                    )
        
        elif data.startswith("summarize_"):
            # Summarize news
            query_text = data.split("_", 1)[1]
            
            await query.message.reply_text(f"📰 Summarizing news about: {query_text}")
            
            # Get news articles
            news_data = self.news_api.search_news(query=query_text, page_size=5)
            
            if news_data.get('success', False):
                articles = news_data.get('articles', [])
                
                if articles:
                    # Summarize articles
                    summary = self.news_api.summarize_news(articles, self.ai_engine)
                    
                    if summary.get('success', False):
                        await query.message.reply_text(
                            f"📰 *News Summary: {query_text}*\n\n{summary.get('summary', '')}",
                            parse_mode="Markdown"
                        )
                    else:
                        await query.message.reply_text(
                            f"❌ Error summarizing news: {summary.get('error', 'Unknown error')}"
                        )
                else:
                    await query.message.reply_text(f"No news found for: {query_text}")
            else:
                await query.message.reply_text(
                    f"❌ Error getting news: {news_data.get('error', 'Unknown error')}"
                )
        
        elif data.startswith("settings_"):
            # Settings options
            setting = data.split("_")[1]
            
            if setting == "language":
                # Language options
                keyboard = [
                    [
                        InlineKeyboardButton("English", callback_data="set_language_english"),
                        InlineKeyboardButton("Spanish", callback_data="set_language_spanish")
                    ],
                    [
                        InlineKeyboardButton("French", callback_data="set_language_french"),
                        InlineKeyboardButton("German", callback_data="set_language_german")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.message.reply_text(
                    "Select your preferred language:",
                    reply_markup=reply_markup
                )
            
            elif setting == "units":
                # Units options
                keyboard = [
                    [
                        InlineKeyboardButton("Metric (°C, m/s)", callback_data="set_units_metric"),
                        InlineKeyboardButton("Imperial (°F, mph)", callback_data="set_units_imperial")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.message.reply_text(
                    "Select your preferred units:",
                    reply_markup=reply_markup
                )
            
            elif setting == "news_country":
                # News country options
                keyboard = [
                    [
                        InlineKeyboardButton("US", callback_data="set_news_country_us"),
                        InlineKeyboardButton("UK", callback_data="set_news_country_gb"),
                        InlineKeyboardButton("Canada", callback_data="set_news_country_ca")
                    ],
                    [
                        InlineKeyboardButton("Australia", callback_data="set_news_country_au"),
                        InlineKeyboardButton("India", callback_data="set_news_country_in"),
                        InlineKeyboardButton("Germany", callback_data="set_news_country_de")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.message.reply_text(
                    "Select your preferred news country:",
                    reply_markup=reply_markup
                )
            
            elif setting == "reset":
                # Reset all settings
                self.memory_manager.save_memory(user_id, "preferences", {})
                
                await query.message.reply_text(
                    "✅ All settings have been reset to default values."
                )
        
        elif data.startswith("set_"):
            # Set specific setting
            parts = data.split("_")
            setting_type = parts[1]
            setting_value = parts[2]
            
            # Get current preferences
            preferences = self.memory_manager.get_memory(user_id, "preferences", {})
            
            # Update preference
            if setting_type == "language":
                preferences["language"] = setting_value.capitalize()
            elif setting_type == "units":
                preferences["units"] = setting_value.capitalize()
            elif setting_type == "news_country":
                preferences["news_country"] = setting_value.upper()
            
            # Save updated preferences
            self.memory_manager.save_memory(user_id, "preferences", preferences)
            
            await query.message.reply_text(
                f"✅ Your {setting_type} preference has been updated to {setting_value.capitalize()}."
            )
    
    async def error_handler(self, update, context):
        """Handle errors."""
        logger.error(f"Error: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An error occurred while processing your request. Please try again later."
            )
    
    def run(self):
        """Run the bot."""
        # Create application
        application = Application.builder().token(self.token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("chat", self.chat_command))
        application.add_handler(CommandHandler("reset", self.reset_command))
        application.add_handler(CommandHandler("finance", self.finance_command))
        application.add_handler(CommandHandler("code", self.code_command))
        application.add_handler(CommandHandler("analyze_code", self.analyze_code_command))
        application.add_handler(CommandHandler("weather", self.weather_command))
        application.add_handler(CommandHandler("news", self.news_command))
        application.add_handler(CommandHandler("settings", self.settings_command))
        application.add_handler(CommandHandler("feedback", self.feedback_command))
        
        # Add message handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Add callback query handler
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Add error handler
        application.add_error_handler(self.error_handler)
        
        # Start the bot
        logger.info("Starting Telegram Bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

def start_bot(components=None):
    """Start the Telegram bot."""
    try:
        bot = TelegramBot()
        bot.run()
    except Exception as e:
        logger.error(f"Error starting Telegram bot: {e}")
        raise

if __name__ == "__main__":
    start_bot()
