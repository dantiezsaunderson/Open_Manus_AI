"""
Enhanced Telegram Integration Module

This module provides improved Telegram integration for the Open Manus AI system,
allowing users to interact with the AI assistant through Telegram.
"""

import logging
import os
import json
import time
import asyncio
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable
import re

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler
)

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedTelegramIntegration:
    """
    Enhanced Telegram Integration for the Open Manus AI system.
    
    This class provides improved Telegram integration with:
    - Seamless conversation with the AI assistant
    - Financial data and analysis commands
    - Multi-agent task delegation
    - User preference management
    - Rich media responses (images, charts, documents)
    - Interactive buttons and menus
    """
    
    # Conversation states
    (
        MAIN_CONVERSATION,
        FINANCIAL_ANALYSIS,
        STOCK_ANALYSIS,
        PORTFOLIO_MANAGEMENT,
        SETTINGS,
        WAITING_FOR_SYMBOL,
        WAITING_FOR_PERIOD,
        WAITING_FOR_SHARES,
        WAITING_FOR_COST_BASIS
    ) = range(9)
    
    def __init__(
        self,
        token: str = None,
        ai_engine = None,
        memory_manager = None,
        conversation_module = None,
        financial_analysis_module = None,
        multi_agent_system = None
    ):
        """
        Initialize the Enhanced Telegram Integration.
        
        Args:
            token (str, optional): Telegram bot token
            ai_engine (AIEngine, optional): AI engine for generating responses
            memory_manager (EnhancedMemoryManager, optional): Memory manager for context and personalization
            conversation_module (EnhancedConversationModule, optional): Conversation module for handling messages
            financial_analysis_module (EnhancedFinancialAnalysis, optional): Financial analysis module
            multi_agent_system (EnhancedMultiAgentSystem, optional): Multi-agent system for task delegation
        """
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("Telegram bot token is required")
        
        self.ai_engine = ai_engine
        self.memory_manager = memory_manager
        self.conversation_module = conversation_module
        self.financial_analysis_module = financial_analysis_module
        self.multi_agent_system = multi_agent_system
        
        self.bot = Bot(token=self.token)
        self.application = Application.builder().token(self.token).build()
        
        # User session data
        self.user_sessions = {}
        
        # Register handlers
        self._register_handlers()
        
        logger.info("Enhanced Telegram Integration initialized")
    
    def _register_handlers(self):
        """Register message and command handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        
        # Financial commands
        self.application.add_handler(CommandHandler("finance", self.finance_command))
        self.application.add_handler(CommandHandler("stock", self.stock_command))
        self.application.add_handler(CommandHandler("portfolio", self.portfolio_command))
        self.application.add_handler(CommandHandler("watchlist", self.watchlist_command))
        self.application.add_handler(CommandHandler("market", self.market_command))
        
        # Multi-agent commands
        self.application.add_handler(CommandHandler("task", self.task_command))
        self.application.add_handler(CommandHandler("agents", self.agents_command))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Conversation handler for financial analysis
        financial_analysis_conv = ConversationHandler(
            entry_points=[CommandHandler("analyze", self.analyze_command)],
            states={
                self.WAITING_FOR_SYMBOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_symbol)],
                self.WAITING_FOR_PERIOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_period)]
            },
            fallbacks=[CommandHandler("cancel", self.cancel_command)]
        )
        self.application.add_handler(financial_analysis_conv)
        
        # Conversation handler for portfolio management
        portfolio_conv = ConversationHandler(
            entry_points=[CommandHandler("add_to_portfolio", self.add_to_portfolio_command)],
            states={
                self.WAITING_FOR_SYMBOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_portfolio_symbol)],
                self.WAITING_FOR_SHARES: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_shares)],
                self.WAITING_FOR_COST_BASIS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_cost_basis)]
            },
            fallbacks=[CommandHandler("cancel", self.cancel_command)]
        )
        self.application.add_handler(portfolio_conv)
        
        # Default message handler (for conversation)
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command."""
        user = update.effective_user
        user_id = str(user.id)
        
        # Initialize user session
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "telegram_id": user_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "conversation_id": None,
                "last_activity": datetime.now().isoformat(),
                "context": {}
            }
        
        # Create user in memory manager if not exists
        if self.memory_manager:
            memory_user = self.memory_manager.get_user(user_id)
            if not memory_user:
                self.memory_manager.create_user(user.first_name)
                self.memory_manager.set_preference(user_id, "telegram", "username", user.username)
        
        # Start a new conversation
        if self.conversation_module:
            conversation = self.conversation_module.start_conversation(user_id)
            self.user_sessions[user_id]["conversation_id"] = conversation["conversation_id"]
        
        # Welcome message
        welcome_text = (
            f"👋 Hello, {user.first_name}! I'm Open Manus AI, your personal AI assistant.\n\n"
            "I can help you with:\n"
            "• General questions and conversations\n"
            "• Financial analysis and stock information\n"
            "• Task automation and research\n\n"
            "Just send me a message or use one of the commands below to get started!\n\n"
            "Type /help to see all available commands."
        )
        
        # Create keyboard with main options
        keyboard = [
            [
                InlineKeyboardButton("💬 Chat", callback_data="chat"),
                InlineKeyboardButton("📊 Finance", callback_data="finance")
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
                InlineKeyboardButton("❓ Help", callback_data="help")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command."""
        help_text = (
            "🤖 *Open Manus AI Commands*\n\n"
            "*General Commands:*\n"
            "/start - Start or restart the bot\n"
            "/help - Show this help message\n"
            "/settings - Manage your preferences\n\n"
            
            "*Financial Commands:*\n"
            "/finance - Financial dashboard\n"
            "/stock [symbol] - Get stock information\n"
            "/analyze - Analyze a stock\n"
            "/portfolio - View your portfolio\n"
            "/watchlist - View your watchlist\n"
            "/market - Get market overview\n"
            "/add_to_portfolio - Add a stock to your portfolio\n\n"
            
            "*Multi-Agent Commands:*\n"
            "/task [description] - Submit a task to the multi-agent system\n"
            "/agents - View active agents\n\n"
            
            "You can also just chat with me normally for general conversation!"
        )
        
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /settings command."""
        user_id = str(update.effective_user.id)
        
        # Get user preferences
        preferences = {}
        if self.memory_manager:
            preferences = self.memory_manager.get_all_preferences(user_id)
        
        # Create settings menu
        settings_text = "⚙️ *Settings*\n\nSelect an option to configure:"
        
        keyboard = [
            [
                InlineKeyboardButton("Communication Style", callback_data="settings_comm_style"),
                InlineKeyboardButton("Detail Level", callback_data="settings_detail_level")
            ],
            [
                InlineKeyboardButton("Financial Preferences", callback_data="settings_financial"),
                InlineKeyboardButton("Notification Settings", callback_data="settings_notifications")
            ],
            [
                InlineKeyboardButton("Clear Data", callback_data="settings_clear_data"),
                InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(settings_text, reply_markup=reply_markup, parse_mode="Markdown")
    
    async def finance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /finance command."""
        finance_text = "📊 *Financial Dashboard*\n\nSelect an option:"
        
        keyboard = [
            [
                InlineKeyboardButton("Market Overview", callback_data="finance_market"),
                InlineKeyboardButton("Stock Analysis", callback_data="finance_stock")
            ],
            [
                InlineKeyboardButton("Portfolio", callback_data="finance_portfolio"),
                InlineKeyboardButton("Watchlist", callback_data="finance_watchlist")
            ],
            [
                InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(finance_text, reply_markup=reply_markup, parse_mode="Markdown")
    
    async def stock_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /stock command."""
        # Check if a symbol was provided
        if context.args and len(context.args) > 0:
            symbol = context.args[0].upper()
            await self._get_stock_info(update, symbol)
        else:
            await update.message.reply_text(
                "Please provide a stock symbol. Example: /stock AAPL"
            )
    
    async def _get_stock_info(self, update: Update, symbol: str):
        """Get and display stock information."""
        if not self.financial_analysis_module:
            await update.message.reply_text("Financial analysis module is not available.")
            return
        
        # Send typing action
        await self.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Get stock data
        stock_data = self.financial_analysis_module.get_stock_data(symbol)
        
        if not stock_data.get("success", False):
            await update.message.reply_text(f"Error getting data for {symbol}: {stock_data.get('error', 'Unknown error')}")
            return
        
        # Format response
        company_name = stock_data.get("company_name", symbol)
        stats = stock_data.get("stats", {})
        
        latest_price = stats.get("latest_price", "N/A")
        price_change = stats.get("price_change", "N/A")
        price_change_pct = stats.get("price_change_pct", "N/A")
        
        # Determine emoji based on price change
        emoji = "🟢" if price_change >= 0 else "🔴"
        
        response = (
            f"*{company_name}* ({symbol})\n\n"
            f"*Price:* ${latest_price:.2f}\n"
            f"*Change:* {emoji} ${price_change:.2f} ({price_change_pct:.2f}%)\n"
            f"*Volume:* {stats.get('volume', 'N/A'):,}\n"
            f"*Avg Volume:* {stats.get('avg_volume', 'N/A'):,}\n\n"
            f"*52W High:* ${stats.get('high_52w', 'N/A'):.2f}\n"
            f"*52W Low:* ${stats.get('low_52w', 'N/A'):.2f}\n"
        )
        
        # Create keyboard with actions
        keyboard = [
            [
                InlineKeyboardButton("📈 Analyze", callback_data=f"analyze_{symbol}"),
                InlineKeyboardButton("👁️ Add to Watchlist", callback_data=f"watchlist_add_{symbol}")
            ],
            [
                InlineKeyboardButton("💼 Add to Portfolio", callback_data=f"portfolio_add_{symbol}"),
                InlineKeyboardButton("🔍 More Info", callback_data=f"stock_more_{symbol}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /analyze command."""
        await update.message.reply_text(
            "Please enter the stock symbol you want to analyze:"
        )
        return self.WAITING_FOR_SYMBOL
    
    async def receive_symbol(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the stock symbol input."""
        symbol = update.message.text.strip().upper()
        context.user_data["analysis_symbol"] = symbol
        
        await update.message.reply_text(
            f"Analyzing {symbol}. Please select the time period:\n\n"
            "1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y"
        )
        return self.WAITING_FOR_PERIOD
    
    async def receive_period(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the time period input."""
        period = update.message.text.strip().lower()
        symbol = context.user_data.get("analysis_symbol")
        
        valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"]
        if period not in valid_periods:
            await update.message.reply_text(
                f"Invalid period. Please select from: {', '.join(valid_periods)}"
            )
            return self.WAITING_FOR_PERIOD
        
        # Send typing action
        await self.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        await update.message.reply_text(f"Analyzing {symbol} for period {period}. Please wait...")
        
        if not self.financial_analysis_module:
            await update.message.reply_text("Financial analysis module is not available.")
            return ConversationHandler.END
        
        # Perform analysis
        analysis_result = self.financial_analysis_module.analyze_stock(symbol, period=period)
        
        if not analysis_result.get("success", False):
            await update.message.reply_text(f"Error analyzing {symbol}: {analysis_result.get('error', 'Unknown error')}")
            return ConversationHandler.END
        
        # Generate chart
        chart_result = self.financial_analysis_module.generate_stock_chart(
            symbol, 
            period=period, 
            chart_type="candle",
            include_volume=True,
            include_indicators=True
        )
        
        # Send analysis summary
        company_info = analysis_result.get("company_info", {})
        performance = analysis_result.get("performance", {})
        technical_indicators = analysis_result.get("technical_indicators", {})
        
        summary = (
            f"*Analysis for {company_info.get('company_name', symbol)} ({symbol})*\n\n"
            f"*Period:* {period}\n\n"
        )
        
        # Add performance data
        if period in performance:
            period_perf = performance[period]
            emoji = "🟢" if period_perf.get("change_pct", 0) >= 0 else "🔴"
            summary += (
                f"*Performance:*\n"
                f"{emoji} {period_perf.get('change_pct', 0):.2f}% "
                f"(${period_perf.get('change', 0):.2f})\n\n"
            )
        
        # Add technical indicators
        if technical_indicators:
            summary += "*Technical Indicators:*\n"
            
            # RSI
            if "rsi" in technical_indicators:
                rsi = technical_indicators["rsi"]
                rsi_emoji = "🟢"
                if rsi.get("signal") == "oversold":
                    rsi_emoji = "🔴"
                elif rsi.get("signal") == "overbought":
                    rsi_emoji = "🟠"
                
                summary += f"RSI: {rsi_emoji} {rsi.get('value', 0):.2f} ({rsi.get('signal', 'neutral')})\n"
            
            # MACD
            if "macd" in technical_indicators:
                macd = technical_indicators["macd"]
                macd_emoji = "🟢" if macd.get("trend") == "bullish" else "🔴"
                
                summary += f"MACD: {macd_emoji} {macd.get('trend', 'neutral')}\n"
            
            # Moving averages
            if "moving_averages" in technical_indicators:
                ma = technical_indicators["moving_averages"]
                if "ma50" in ma:
                    ma50 = ma["ma50"]
                    ma50_emoji = "🟢" if ma50.get("signal") == "bullish" else "🔴"
                    summary += f"MA50: {ma50_emoji} {ma50.get('signal', 'neutral')}\n"
            
            summary += "\n"
        
        # Add recommendation
        if "recommendation" in analysis_result:
            rec = analysis_result["recommendation"]
            rec_emoji = "🟢"
            if rec.get("rating") == "sell":
                rec_emoji = "🔴"
            elif rec.get("rating") == "hold":
                rec_emoji = "🟠"
            
            summary += (
                f"*Recommendation:*\n"
                f"{rec_emoji} {rec.get('rating', 'N/A').upper()}\n"
                f"Target: ${rec.get('target_price', 0):.2f}\n\n"
            )
        
        # Send summary
        await update.message.reply_text(summary, parse_mode="Markdown")
        
        # Send chart if available
        if chart_result.get("success", False) and "filepath" in chart_result:
            with open(chart_result["filepath"], "rb") as chart_file:
                await update.message.reply_photo(
                    photo=chart_file,
                    caption=f"{symbol} Chart ({period})"
                )
        
        # Create keyboard with actions
        keyboard = [
            [
                InlineKeyboardButton("👁️ Add to Watchlist", callback_data=f"watchlist_add_{symbol}"),
                InlineKeyboardButton("💼 Add to Portfolio", callback_data=f"portfolio_add_{symbol}")
            ],
            [
                InlineKeyboardButton("📊 Financial Dashboard", callback_data="finance"),
                InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "What would you like to do next?",
            reply_markup=reply_markup
        )
        
        return ConversationHandler.END
    
    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /portfolio command."""
        user_id = str(update.effective_user.id)
        
        # Get portfolio from memory manager
        portfolio = []
        if self.memory_manager:
            portfolio = self.memory_manager.get_preference(user_id, "financial", "portfolio", [])
        
        if not portfolio:
            # Create keyboard with actions
            keyboard = [
                [
                    InlineKeyboardButton("Add to Portfolio", callback_data="portfolio_add"),
                    InlineKeyboardButton("Financial Dashboard", callback_data="finance")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "Your portfolio is empty. Add stocks to your portfolio to track them.",
                reply_markup=reply_markup
            )
            return
        
        # Send typing action
        await self.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Analyze portfolio
        if self.financial_analysis_module:
            portfolio_analysis = self.financial_analysis_module.analyze_portfolio(portfolio)
            
            if portfolio_analysis.get("success", False):
                # Format response
                total_value = portfolio_analysis.get("total_value", 0)
                total_cost = portfolio_analysis.get("total_cost", 0)
                gain_loss = portfolio_analysis.get("gain_loss", 0)
                gain_loss_pct = portfolio_analysis.get("gain_loss_pct", 0)
                
                emoji = "🟢" if gain_loss >= 0 else "🔴"
                
                response = (
                    f"*Your Portfolio*\n\n"
                    f"*Total Value:* ${total_value:.2f}\n"
                    f"*Total Cost:* ${total_cost:.2f}\n"
                    f"*Gain/Loss:* {emoji} ${gain_loss:.2f} ({gain_loss_pct:.2f}%)\n\n"
                    f"*Holdings:*\n"
                )
                
                # Add holdings
                for holding in portfolio_analysis.get("holdings", []):
                    if holding.get("success", False):
                        h_emoji = "🟢" if holding.get("gain_loss_pct", 0) >= 0 else "🔴"
                        response += (
                            f"*{holding['symbol']}*: {holding['shares']} shares\n"
                            f"  Current: ${holding['latest_price']:.2f} | "
                            f"Value: ${holding['current_value']:.2f}\n"
                            f"  {h_emoji} {holding['gain_loss_pct']:.2f}% "
                            f"(${holding['gain_loss']:.2f})\n\n"
                        )
                
                # Create keyboard with actions
                keyboard = [
                    [
                        InlineKeyboardButton("Add to Portfolio", callback_data="portfolio_add"),
                        InlineKeyboardButton("Remove from Portfolio", callback_data="portfolio_remove")
                    ],
                    [
                        InlineKeyboardButton("Financial Dashboard", callback_data="finance"),
                        InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")
            else:
                await update.message.reply_text(f"Error analyzing portfolio: {portfolio_analysis.get('error', 'Unknown error')}")
        else:
            # Basic portfolio display without analysis
            response = "*Your Portfolio*\n\n"
            
            for item in portfolio:
                response += (
                    f"*{item['symbol']}*: {item['shares']} shares\n"
                    f"  Cost Basis: ${item['cost_basis']:.2f}\n\n"
                )
            
            # Create keyboard with actions
            keyboard = [
                [
                    InlineKeyboardButton("Add to Portfolio", callback_data="portfolio_add"),
                    InlineKeyboardButton("Remove from Portfolio", callback_data="portfolio_remove")
                ],
                [
                    InlineKeyboardButton("Financial Dashboard", callback_data="finance"),
                    InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")
    
    async def add_to_portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /add_to_portfolio command."""
        await update.message.reply_text(
            "Please enter the stock symbol you want to add to your portfolio:"
        )
        return self.WAITING_FOR_SYMBOL
    
    async def receive_portfolio_symbol(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the portfolio stock symbol input."""
        symbol = update.message.text.strip().upper()
        context.user_data["portfolio_symbol"] = symbol
        
        await update.message.reply_text(
            f"Adding {symbol} to portfolio. Please enter the number of shares:"
        )
        return self.WAITING_FOR_SHARES
    
    async def receive_shares(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the shares input."""
        try:
            shares = float(update.message.text.strip())
            if shares <= 0:
                raise ValueError("Shares must be positive")
            
            context.user_data["portfolio_shares"] = shares
            
            await update.message.reply_text(
                f"Please enter the cost basis per share (purchase price):"
            )
            return self.WAITING_FOR_COST_BASIS
        except ValueError:
            await update.message.reply_text(
                "Please enter a valid number of shares (must be positive):"
            )
            return self.WAITING_FOR_SHARES
    
    async def receive_cost_basis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the cost basis input."""
        try:
            cost_basis = float(update.message.text.strip())
            if cost_basis <= 0:
                raise ValueError("Cost basis must be positive")
            
            symbol = context.user_data.get("portfolio_symbol")
            shares = context.user_data.get("portfolio_shares")
            
            # Add to portfolio
            user_id = str(update.effective_user.id)
            
            if self.memory_manager:
                # Get existing portfolio
                portfolio = self.memory_manager.get_preference(user_id, "financial", "portfolio", [])
                
                # Check if symbol already exists
                for i, item in enumerate(portfolio):
                    if item["symbol"] == symbol:
                        # Update existing entry
                        portfolio[i] = {
                            "symbol": symbol,
                            "shares": shares,
                            "cost_basis": cost_basis,
                            "date_added": datetime.now().isoformat()
                        }
                        break
                else:
                    # Add new entry
                    portfolio.append({
                        "symbol": symbol,
                        "shares": shares,
                        "cost_basis": cost_basis,
                        "date_added": datetime.now().isoformat()
                    })
                
                # Save updated portfolio
                self.memory_manager.set_preference(user_id, "financial", "portfolio", portfolio)
            
            await update.message.reply_text(
                f"Added {shares} shares of {symbol} to your portfolio with a cost basis of ${cost_basis:.2f} per share."
            )
            
            # Create keyboard with actions
            keyboard = [
                [
                    InlineKeyboardButton("View Portfolio", callback_data="finance_portfolio"),
                    InlineKeyboardButton("Add Another Stock", callback_data="portfolio_add")
                ],
                [
                    InlineKeyboardButton("Financial Dashboard", callback_data="finance"),
                    InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "What would you like to do next?",
                reply_markup=reply_markup
            )
            
            return ConversationHandler.END
        except ValueError:
            await update.message.reply_text(
                "Please enter a valid cost basis (must be positive):"
            )
            return self.WAITING_FOR_COST_BASIS
    
    async def watchlist_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /watchlist command."""
        user_id = str(update.effective_user.id)
        
        # Get watchlist from memory manager
        watchlist = []
        if self.memory_manager:
            watchlist = self.memory_manager.get_preference(user_id, "financial", "watchlist", [])
        
        if not watchlist:
            # Create keyboard with actions
            keyboard = [
                [
                    InlineKeyboardButton("Add to Watchlist", callback_data="watchlist_add"),
                    InlineKeyboardButton("Financial Dashboard", callback_data="finance")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "Your watchlist is empty. Add stocks to your watchlist to track them.",
                reply_markup=reply_markup
            )
            return
        
        # Send typing action
        await self.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Get data for watchlist symbols
        response = "*Your Watchlist*\n\n"
        
        if self.financial_analysis_module:
            for symbol in watchlist:
                stock_data = self.financial_analysis_module.get_stock_data(symbol)
                
                if stock_data.get("success", False) and "stats" in stock_data:
                    company_name = stock_data.get("company_name", symbol)
                    stats = stock_data["stats"]
                    
                    emoji = "🟢" if stats.get("price_change_pct", 0) >= 0 else "🔴"
                    
                    response += (
                        f"*{company_name}* ({symbol})\n"
                        f"${stats.get('latest_price', 0):.2f} | "
                        f"{emoji} {stats.get('price_change_pct', 0):.2f}%\n\n"
                    )
                else:
                    response += f"*{symbol}*: Data not available\n\n"
        else:
            # Basic watchlist without data
            for symbol in watchlist:
                response += f"*{symbol}*\n\n"
        
        # Create keyboard with actions
        keyboard = [
            [
                InlineKeyboardButton("Add to Watchlist", callback_data="watchlist_add"),
                InlineKeyboardButton("Remove from Watchlist", callback_data="watchlist_remove")
            ],
            [
                InlineKeyboardButton("Financial Dashboard", callback_data="finance"),
                InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")
    
    async def market_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /market command."""
        # Send typing action
        await self.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        if not self.financial_analysis_module:
            await update.message.reply_text("Financial analysis module is not available.")
            return
        
        # Get market data
        indices = ["^GSPC", "^DJI", "^IXIC"]  # S&P 500, Dow Jones, NASDAQ
        index_names = ["S&P 500", "Dow Jones", "NASDAQ"]
        
        response = "*Market Overview*\n\n"
        
        for i, index in enumerate(indices):
            index_data = self.financial_analysis_module.get_stock_data(index)
            
            if index_data.get("success", False) and "stats" in index_data:
                stats = index_data["stats"]
                
                emoji = "🟢" if stats.get("price_change_pct", 0) >= 0 else "🔴"
                
                response += (
                    f"*{index_names[i]}*\n"
                    f"${stats.get('latest_price', 0):.2f} | "
                    f"{emoji} {stats.get('price_change_pct', 0):.2f}%\n\n"
                )
            else:
                response += f"*{index_names[i]}*: Data not available\n\n"
        
        # Generate S&P 500 chart
        chart_result = self.financial_analysis_module.generate_stock_chart(
            "^GSPC", 
            period="1mo", 
            chart_type="line",
            include_volume=True,
            include_indicators=False
        )
        
        # Create keyboard with actions
        keyboard = [
            [
                InlineKeyboardButton("Stock Analysis", callback_data="finance_stock"),
                InlineKeyboardButton("Portfolio", callback_data="finance_portfolio")
            ],
            [
                InlineKeyboardButton("Financial Dashboard", callback_data="finance"),
                InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")
        
        # Send chart if available
        if chart_result.get("success", False) and "filepath" in chart_result:
            with open(chart_result["filepath"], "rb") as chart_file:
                await update.message.reply_photo(
                    photo=chart_file,
                    caption="S&P 500 (1 Month)"
                )
    
    async def task_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /task command."""
        if not self.multi_agent_system:
            await update.message.reply_text("Multi-agent system is not available.")
            return
        
        # Check if a task description was provided
        if context.args and len(" ".join(context.args)) > 0:
            task_description = " ".join(context.args)
            
            # Send typing action
            await self.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            await update.message.reply_text(f"Processing task: {task_description}")
            
            # Submit task to multi-agent system
            task_params = {
                "task_type": "general",
                "query": task_description
            }
            
            task_id = self.multi_agent_system.assign_task(task_params)
            
            if task_id:
                # Store task ID in user session
                user_id = str(update.effective_user.id)
                if user_id in self.user_sessions:
                    self.user_sessions[user_id]["last_task_id"] = task_id
                
                await update.message.reply_text(
                    f"Task submitted successfully! Task ID: {task_id}\n\n"
                    "I'll notify you when the task is complete."
                )
                
                # Start a background task to check for completion
                threading.Thread(
                    target=self._check_task_completion,
                    args=(task_id, update.effective_chat.id)
                ).start()
            else:
                await update.message.reply_text("Failed to submit task.")
        else:
            # Create task submission form
            task_types = [
                "Research",
                "Code Generation",
                "Stock Analysis",
                "Portfolio Analysis",
                "Technical Analysis",
                "Fundamental Analysis"
            ]
            
            keyboard = []
            for task_type in task_types:
                keyboard.append([InlineKeyboardButton(task_type, callback_data=f"task_type_{task_type.lower().replace(' ', '_')}")])
            
            keyboard.append([InlineKeyboardButton("Cancel", callback_data="main_menu")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "Please select a task type or use /task [description] to submit a task directly:",
                reply_markup=reply_markup
            )
    
    def _check_task_completion(self, task_id, chat_id):
        """Check for task completion in a background thread."""
        if not self.multi_agent_system:
            return
        
        max_checks = 60  # Maximum number of checks (10 minutes at 10-second intervals)
        check_interval = 10  # Seconds between checks
        
        for _ in range(max_checks):
            time.sleep(check_interval)
            
            task_result = self.multi_agent_system.get_task_result(task_id)
            
            if task_result.get("status") == "completed":
                # Task completed, send notification
                result = task_result.get("result", {})
                
                # Format result based on type
                if "analysis" in result:
                    message = f"Task {task_id} completed!\n\nAnalysis results:"
                    result_text = json.dumps(result["analysis"], indent=2)
                elif "code" in result:
                    message = f"Task {task_id} completed!\n\nGenerated code:"
                    result_text = result["code"]
                elif "research" in result:
                    message = f"Task {task_id} completed!\n\nResearch results:"
                    result_text = result["research"]
                elif "summary" in result:
                    message = f"Task {task_id} completed!"
                    result_text = result["summary"]
                else:
                    message = f"Task {task_id} completed!"
                    result_text = json.dumps(result, indent=2)
                
                # Send notification
                asyncio.run(self._send_task_completion(chat_id, message, result_text))
                return
            elif task_result.get("status") == "failed":
                # Task failed, send notification
                error = task_result.get("error", "Unknown error")
                asyncio.run(self._send_task_completion(
                    chat_id,
                    f"Task {task_id} failed: {error}",
                    None
                ))
                return
        
        # If we get here, the task is still running after max_checks
        asyncio.run(self._send_task_completion(
            chat_id,
            f"Task {task_id} is still running. You can check its status with /task_status {task_id}",
            None
        ))
    
    async def _send_task_completion(self, chat_id, message, result_text):
        """Send task completion notification."""
        await self.bot.send_message(chat_id=chat_id, text=message)
        
        if result_text:
            # If result is too long, send as a file
            if len(result_text) > 4000:
                # Create a temporary file
                file_path = f"/tmp/task_result_{int(time.time())}.txt"
                with open(file_path, "w") as f:
                    f.write(result_text)
                
                # Send file
                with open(file_path, "rb") as f:
                    await self.bot.send_document(
                        chat_id=chat_id,
                        document=f,
                        filename="task_result.txt",
                        caption="Task result (full details)"
                    )
                
                # Clean up
                os.remove(file_path)
            else:
                # Send as text
                await self.bot.send_message(chat_id=chat_id, text=result_text)
    
    async def agents_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /agents command."""
        if not self.multi_agent_system:
            await update.message.reply_text("Multi-agent system is not available.")
            return
        
        # Get system status
        system_status = self.multi_agent_system.get_system_status()
        
        response = (
            f"*Multi-Agent System Status*\n\n"
            f"*Active Agents:* {system_status.get('agent_count', 0)}\n"
            f"*Active Tasks:* {system_status.get('active_tasks', 0)}\n\n"
            f"*Agents:*\n"
        )
        
        for agent in system_status.get("agents", []):
            response += (
                f"*{agent.get('name', 'Unknown')}* ({agent.get('type', 'Unknown')})\n"
                f"Status: {agent.get('status', 'Unknown')}\n"
                f"Queue: {agent.get('queue_size', 0)} | "
                f"Active: {agent.get('active_tasks', 0)}\n\n"
            )
        
        await update.message.reply_text(response, parse_mode="Markdown")
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /cancel command."""
        await update.message.reply_text(
            "Operation cancelled."
        )
        return ConversationHandler.END
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks."""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        user_id = str(update.effective_user.id)
        
        # Main menu options
        if callback_data == "main_menu":
            keyboard = [
                [
                    InlineKeyboardButton("💬 Chat", callback_data="chat"),
                    InlineKeyboardButton("📊 Finance", callback_data="finance")
                ],
                [
                    InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
                    InlineKeyboardButton("❓ Help", callback_data="help")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "What would you like to do?",
                reply_markup=reply_markup
            )
        
        elif callback_data == "chat":
            await query.edit_message_text(
                "You can chat with me by simply sending a message. What would you like to talk about?"
            )
        
        elif callback_data == "help":
            help_text = (
                "🤖 *Open Manus AI Commands*\n\n"
                "*General Commands:*\n"
                "/start - Start or restart the bot\n"
                "/help - Show this help message\n"
                "/settings - Manage your preferences\n\n"
                
                "*Financial Commands:*\n"
                "/finance - Financial dashboard\n"
                "/stock [symbol] - Get stock information\n"
                "/analyze - Analyze a stock\n"
                "/portfolio - View your portfolio\n"
                "/watchlist - View your watchlist\n"
                "/market - Get market overview\n"
                "/add_to_portfolio - Add a stock to your portfolio\n\n"
                
                "*Multi-Agent Commands:*\n"
                "/task [description] - Submit a task to the multi-agent system\n"
                "/agents - View active agents\n\n"
                
                "You can also just chat with me normally for general conversation!"
            )
            
            await query.edit_message_text(help_text, parse_mode="Markdown")
        
        # Finance options
        elif callback_data == "finance":
            await self.finance_command(update, context)
        
        elif callback_data == "finance_market":
            # Simulate market command
            message = update.effective_message
            update.effective_message = message
            await self.market_command(update, context)
        
        elif callback_data == "finance_stock":
            await query.edit_message_text(
                "Please use /stock [symbol] to get information about a specific stock.\n\n"
                "Example: /stock AAPL"
            )
        
        elif callback_data == "finance_portfolio":
            # Simulate portfolio command
            message = update.effective_message
            update.effective_message = message
            await self.portfolio_command(update, context)
        
        elif callback_data == "finance_watchlist":
            # Simulate watchlist command
            message = update.effective_message
            update.effective_message = message
            await self.watchlist_command(update, context)
        
        # Portfolio options
        elif callback_data == "portfolio_add":
            await query.edit_message_text(
                "Please use /add_to_portfolio to add a stock to your portfolio."
            )
        
        elif callback_data.startswith("portfolio_add_"):
            symbol = callback_data.split("_")[-1]
            context.user_data["portfolio_symbol"] = symbol
            
            await query.edit_message_text(
                f"Adding {symbol} to portfolio. Please enter the number of shares:"
            )
            
            # Set conversation state
            context.user_data["conversation_state"] = self.WAITING_FOR_SHARES
        
        elif callback_data == "portfolio_remove":
            # Get portfolio from memory manager
            portfolio = []
            if self.memory_manager:
                portfolio = self.memory_manager.get_preference(user_id, "financial", "portfolio", [])
            
            if not portfolio:
                await query.edit_message_text("Your portfolio is empty.")
                return
            
            # Create keyboard with symbols to remove
            keyboard = []
            for item in portfolio:
                symbol = item["symbol"]
                keyboard.append([InlineKeyboardButton(symbol, callback_data=f"portfolio_remove_{symbol}")])
            
            keyboard.append([InlineKeyboardButton("Cancel", callback_data="finance_portfolio")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "Select a stock to remove from your portfolio:",
                reply_markup=reply_markup
            )
        
        elif callback_data.startswith("portfolio_remove_"):
            symbol = callback_data.split("_")[-1]
            
            # Remove from portfolio
            if self.memory_manager:
                portfolio = self.memory_manager.get_preference(user_id, "financial", "portfolio", [])
                portfolio = [item for item in portfolio if item["symbol"] != symbol]
                self.memory_manager.set_preference(user_id, "financial", "portfolio", portfolio)
            
            await query.edit_message_text(f"Removed {symbol} from your portfolio.")
        
        # Watchlist options
        elif callback_data == "watchlist_add":
            await query.edit_message_text(
                "Please enter the stock symbol you want to add to your watchlist:"
            )
            
            # Set conversation state
            context.user_data["conversation_state"] = "waiting_for_watchlist_symbol"
        
        elif callback_data.startswith("watchlist_add_"):
            symbol = callback_data.split("_")[-1]
            
            # Add to watchlist
            if self.memory_manager:
                watchlist = self.memory_manager.get_preference(user_id, "financial", "watchlist", [])
                if symbol not in watchlist:
                    watchlist.append(symbol)
                    self.memory_manager.set_preference(user_id, "financial", "watchlist", watchlist)
                    await query.edit_message_text(f"Added {symbol} to your watchlist.")
                else:
                    await query.edit_message_text(f"{symbol} is already in your watchlist.")
            else:
                await query.edit_message_text("Memory manager is not available.")
        
        elif callback_data == "watchlist_remove":
            # Get watchlist from memory manager
            watchlist = []
            if self.memory_manager:
                watchlist = self.memory_manager.get_preference(user_id, "financial", "watchlist", [])
            
            if not watchlist:
                await query.edit_message_text("Your watchlist is empty.")
                return
            
            # Create keyboard with symbols to remove
            keyboard = []
            for symbol in watchlist:
                keyboard.append([InlineKeyboardButton(symbol, callback_data=f"watchlist_remove_{symbol}")])
            
            keyboard.append([InlineKeyboardButton("Cancel", callback_data="finance_watchlist")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "Select a stock to remove from your watchlist:",
                reply_markup=reply_markup
            )
        
        elif callback_data.startswith("watchlist_remove_"):
            symbol = callback_data.split("_")[-1]
            
            # Remove from watchlist
            if self.memory_manager:
                watchlist = self.memory_manager.get_preference(user_id, "financial", "watchlist", [])
                if symbol in watchlist:
                    watchlist.remove(symbol)
                    self.memory_manager.set_preference(user_id, "financial", "watchlist", watchlist)
                    await query.edit_message_text(f"Removed {symbol} from your watchlist.")
                else:
                    await query.edit_message_text(f"{symbol} is not in your watchlist.")
            else:
                await query.edit_message_text("Memory manager is not available.")
        
        # Stock analysis options
        elif callback_data.startswith("analyze_"):
            symbol = callback_data.split("_")[-1]
            context.user_data["analysis_symbol"] = symbol
            
            # Create keyboard with period options
            keyboard = [
                [
                    InlineKeyboardButton("1 Day", callback_data=f"analyze_period_{symbol}_1d"),
                    InlineKeyboardButton("5 Days", callback_data=f"analyze_period_{symbol}_5d"),
                    InlineKeyboardButton("1 Month", callback_data=f"analyze_period_{symbol}_1mo")
                ],
                [
                    InlineKeyboardButton("3 Months", callback_data=f"analyze_period_{symbol}_3mo"),
                    InlineKeyboardButton("6 Months", callback_data=f"analyze_period_{symbol}_6mo"),
                    InlineKeyboardButton("1 Year", callback_data=f"analyze_period_{symbol}_1y")
                ],
                [
                    InlineKeyboardButton("Cancel", callback_data="finance")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"Select a time period to analyze {symbol}:",
                reply_markup=reply_markup
            )
        
        elif callback_data.startswith("analyze_period_"):
            parts = callback_data.split("_")
            symbol = parts[2]
            period = parts[3]
            
            # Simulate period input
            context.user_data["analysis_symbol"] = symbol
            update.effective_message = query.message
            update.effective_message.text = period
            
            await self.receive_period(update, context)
        
        # Stock more info options
        elif callback_data.startswith("stock_more_"):
            symbol = callback_data.split("_")[-1]
            
            # Send typing action
            await self.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            if not self.financial_analysis_module:
                await query.edit_message_text("Financial analysis module is not available.")
                return
            
            # Get more detailed stock data
            stock_data = self.financial_analysis_module.get_stock_data(symbol, include_extended=True)
            
            if not stock_data.get("success", False):
                await query.edit_message_text(f"Error getting data for {symbol}: {stock_data.get('error', 'Unknown error')}")
                return
            
            # Format response
            company_info = stock_data.get("company_info", {})
            stats = stock_data.get("stats", {})
            fundamentals = stock_data.get("fundamentals", {})
            
            response = (
                f"*{company_info.get('company_name', symbol)}* ({symbol})\n\n"
                f"*Exchange:* {company_info.get('exchange', 'Unknown')}\n"
                f"*Industry:* {company_info.get('industry', 'Unknown')}\n"
                f"*Sector:* {company_info.get('sector', 'Unknown')}\n\n"
                
                f"*Price:* ${stats.get('latest_price', 0):.2f}\n"
                f"*Market Cap:* ${stats.get('market_cap', 0)/1000000000:.2f}B\n"
                f"*P/E Ratio:* {fundamentals.get('pe_ratio', 'N/A')}\n"
                f"*Dividend Yield:* {fundamentals.get('dividend_yield', 0):.2f}%\n\n"
                
                f"*52W High:* ${stats.get('high_52w', 0):.2f}\n"
                f"*52W Low:* ${stats.get('low_52w', 0):.2f}\n"
                f"*Avg Volume:* {stats.get('avg_volume', 0):,}\n\n"
                
                f"*Beta:* {fundamentals.get('beta', 'N/A')}\n"
                f"*EPS:* ${fundamentals.get('eps', 0):.2f}\n"
            )
            
            # Create keyboard with actions
            keyboard = [
                [
                    InlineKeyboardButton("📈 Analyze", callback_data=f"analyze_{symbol}"),
                    InlineKeyboardButton("👁️ Add to Watchlist", callback_data=f"watchlist_add_{symbol}")
                ],
                [
                    InlineKeyboardButton("💼 Add to Portfolio", callback_data=f"portfolio_add_{symbol}"),
                    InlineKeyboardButton("Back", callback_data=f"stock_{symbol}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(response, reply_markup=reply_markup, parse_mode="Markdown")
        
        # Settings options
        elif callback_data == "settings":
            await self.settings_command(update, context)
        
        elif callback_data == "settings_comm_style":
            # Communication style settings
            styles = ["conversational", "concise", "detailed", "technical"]
            
            # Get current style
            current_style = "conversational"
            if self.memory_manager:
                current_style = self.memory_manager.get_preference(
                    user_id, "communication", "style", "conversational"
                )
            
            # Create keyboard with style options
            keyboard = []
            for style in styles:
                display_style = style.capitalize()
                if style == current_style:
                    display_style += " ✓"
                keyboard.append([InlineKeyboardButton(display_style, callback_data=f"set_comm_style_{style}")])
            
            keyboard.append([InlineKeyboardButton("Back to Settings", callback_data="settings")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "Select your preferred communication style:",
                reply_markup=reply_markup
            )
        
        elif callback_data.startswith("set_comm_style_"):
            style = callback_data.split("_")[-1]
            
            if self.memory_manager:
                self.memory_manager.set_preference(user_id, "communication", "style", style)
                await query.edit_message_text(f"Communication style set to {style.capitalize()}.")
            else:
                await query.edit_message_text("Memory manager is not available.")
        
        elif callback_data == "settings_detail_level":
            # Detail level settings
            levels = ["minimal", "balanced", "comprehensive"]
            
            # Get current level
            current_level = "balanced"
            if self.memory_manager:
                current_level = self.memory_manager.get_preference(
                    user_id, "communication", "detail_level", "balanced"
                )
            
            # Create keyboard with level options
            keyboard = []
            for level in levels:
                display_level = level.capitalize()
                if level == current_level:
                    display_level += " ✓"
                keyboard.append([InlineKeyboardButton(display_level, callback_data=f"set_detail_level_{level}")])
            
            keyboard.append([InlineKeyboardButton("Back to Settings", callback_data="settings")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "Select your preferred detail level:",
                reply_markup=reply_markup
            )
        
        elif callback_data.startswith("set_detail_level_"):
            level = callback_data.split("_")[-1]
            
            if self.memory_manager:
                self.memory_manager.set_preference(user_id, "communication", "detail_level", level)
                await query.edit_message_text(f"Detail level set to {level.capitalize()}.")
            else:
                await query.edit_message_text("Memory manager is not available.")
        
        elif callback_data == "settings_financial":
            # Financial preferences settings
            keyboard = [
                [
                    InlineKeyboardButton("Risk Tolerance", callback_data="settings_risk"),
                    InlineKeyboardButton("Investment Horizon", callback_data="settings_horizon")
                ],
                [
                    InlineKeyboardButton("Preferred Sectors", callback_data="settings_sectors"),
                    InlineKeyboardButton("Back to Settings", callback_data="settings")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "Select a financial preference to configure:",
                reply_markup=reply_markup
            )
        
        elif callback_data == "settings_risk":
            # Risk tolerance settings
            risk_levels = ["conservative", "moderate", "aggressive"]
            
            # Get current level
            current_level = "moderate"
            if self.memory_manager:
                current_level = self.memory_manager.get_preference(
                    user_id, "financial", "risk_tolerance", "moderate"
                )
            
            # Create keyboard with level options
            keyboard = []
            for level in risk_levels:
                display_level = level.capitalize()
                if level == current_level:
                    display_level += " ✓"
                keyboard.append([InlineKeyboardButton(display_level, callback_data=f"set_risk_{level}")])
            
            keyboard.append([InlineKeyboardButton("Back to Financial Settings", callback_data="settings_financial")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "Select your risk tolerance:",
                reply_markup=reply_markup
            )
        
        elif callback_data.startswith("set_risk_"):
            level = callback_data.split("_")[-1]
            
            if self.memory_manager:
                self.memory_manager.set_preference(user_id, "financial", "risk_tolerance", level)
                await query.edit_message_text(f"Risk tolerance set to {level.capitalize()}.")
            else:
                await query.edit_message_text("Memory manager is not available.")
        
        elif callback_data == "settings_clear_data":
            # Clear data confirmation
            keyboard = [
                [
                    InlineKeyboardButton("Yes, Clear My Data", callback_data="confirm_clear_data"),
                    InlineKeyboardButton("No, Cancel", callback_data="settings")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "⚠️ Are you sure you want to clear all your data? This action cannot be undone.",
                reply_markup=reply_markup
            )
        
        elif callback_data == "confirm_clear_data":
            if self.memory_manager:
                success = self.memory_manager.clear_user_data(user_id)
                if success:
                    # Reset user session
                    if user_id in self.user_sessions:
                        self.user_sessions[user_id] = {
                            "telegram_id": user_id,
                            "username": update.effective_user.username,
                            "first_name": update.effective_user.first_name,
                            "last_name": update.effective_user.last_name,
                            "conversation_id": None,
                            "last_activity": datetime.now().isoformat(),
                            "context": {}
                        }
                    
                    await query.edit_message_text("Your data has been cleared successfully.")
                else:
                    await query.edit_message_text("Failed to clear your data. Please try again.")
            else:
                await query.edit_message_text("Memory manager is not available.")
        
        # Task options
        elif callback_data.startswith("task_type_"):
            task_type = callback_data.split("_")[-1]
            
            # Store task type in user data
            context.user_data["task_type"] = task_type
            
            await query.edit_message_text(
                f"You selected task type: {task_type.replace('_', ' ').capitalize()}\n\n"
                "Please describe your task in detail:"
            )
            
            # Set conversation state
            context.user_data["conversation_state"] = "waiting_for_task_description"
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages."""
        user_id = str(update.effective_user.id)
        message_text = update.message.text
        
        # Check if we're in a special conversation state
        if "conversation_state" in context.user_data:
            state = context.user_data["conversation_state"]
            
            if state == "waiting_for_watchlist_symbol":
                # Handle watchlist symbol input
                symbol = message_text.strip().upper()
                
                # Add to watchlist
                if self.memory_manager:
                    watchlist = self.memory_manager.get_preference(user_id, "financial", "watchlist", [])
                    if symbol not in watchlist:
                        watchlist.append(symbol)
                        self.memory_manager.set_preference(user_id, "financial", "watchlist", watchlist)
                        await update.message.reply_text(f"Added {symbol} to your watchlist.")
                    else:
                        await update.message.reply_text(f"{symbol} is already in your watchlist.")
                else:
                    await update.message.reply_text("Memory manager is not available.")
                
                # Clear conversation state
                context.user_data.pop("conversation_state", None)
                return
            
            elif state == "waiting_for_task_description":
                # Handle task description input
                task_description = message_text
                task_type = context.user_data.get("task_type", "general")
                
                # Send typing action
                await self.bot.send_chat_action(
                    chat_id=update.effective_chat.id,
                    action="typing"
                )
                
                await update.message.reply_text(f"Processing {task_type} task: {task_description}")
                
                if not self.multi_agent_system:
                    await update.message.reply_text("Multi-agent system is not available.")
                    context.user_data.pop("conversation_state", None)
                    return
                
                # Prepare task parameters based on type
                task_params = {
                    "task_type": task_type,
                    "query": task_description
                }
                
                # Determine agent type based on task type
                agent_type = None
                if task_type == "research":
                    agent_type = "research"
                elif task_type in ["code_generation", "code_analysis"]:
                    agent_type = "coding"
                elif task_type == "stock_analysis":
                    agent_type = "financial"
                elif task_type == "technical_analysis":
                    agent_type = "technical_analysis"
                elif task_type == "fundamental_analysis":
                    agent_type = "fundamental_analysis"
                
                # Submit task
                task_id = self.multi_agent_system.assign_task(task_params, agent_type=agent_type)
                
                if task_id:
                    # Store task ID in user session
                    if user_id in self.user_sessions:
                        self.user_sessions[user_id]["last_task_id"] = task_id
                    
                    await update.message.reply_text(
                        f"Task submitted successfully! Task ID: {task_id}\n\n"
                        "I'll notify you when the task is complete."
                    )
                    
                    # Start a background task to check for completion
                    threading.Thread(
                        target=self._check_task_completion,
                        args=(task_id, update.effective_chat.id)
                    ).start()
                else:
                    await update.message.reply_text("Failed to submit task.")
                
                # Clear conversation state
                context.user_data.pop("conversation_state", None)
                return
        
        # Initialize user session if not exists
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "telegram_id": user_id,
                "username": update.effective_user.username,
                "first_name": update.effective_user.first_name,
                "last_name": update.effective_user.last_name,
                "conversation_id": None,
                "last_activity": datetime.now().isoformat(),
                "context": {}
            }
        
        # Create user in memory manager if not exists
        if self.memory_manager:
            memory_user = self.memory_manager.get_user(user_id)
            if not memory_user:
                self.memory_manager.create_user(update.effective_user.first_name)
                self.memory_manager.set_preference(user_id, "telegram", "username", update.effective_user.username)
        
        # Start a new conversation if needed
        if not self.user_sessions[user_id]["conversation_id"] and self.conversation_module:
            conversation = self.conversation_module.start_conversation(user_id)
            self.user_sessions[user_id]["conversation_id"] = conversation["conversation_id"]
        
        # Send typing action
        await self.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Process message with conversation module
        if self.conversation_module and self.user_sessions[user_id]["conversation_id"]:
            response = self.conversation_module.process_message(
                self.user_sessions[user_id]["conversation_id"],
                message_text
            )
            
            if response.get("success", False) and "response" in response:
                await update.message.reply_text(response["response"])
            else:
                # Fallback to AI engine if conversation module fails
                if self.ai_engine:
                    ai_response = self.ai_engine.generate_response(message_text)
                    await update.message.reply_text(ai_response)
                else:
                    await update.message.reply_text("I'm sorry, I couldn't process your message.")
        else:
            # Fallback to AI engine if conversation module is not available
            if self.ai_engine:
                ai_response = self.ai_engine.generate_response(message_text)
                await update.message.reply_text(ai_response)
            else:
                await update.message.reply_text("I'm sorry, I couldn't process your message.")
        
        # Update last activity
        self.user_sessions[user_id]["last_activity"] = datetime.now().isoformat()
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors."""
        logger.error(f"Update {update} caused error {context.error}")
        
        # Send error message to user
        if update and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="An error occurred while processing your request. Please try again later."
            )
    
    def start(self):
        """Start the bot."""
        logger.info("Starting Telegram bot")
        self.application.run_polling()
    
    def start_webhook(self, webhook_url: str, port: int = 8443):
        """Start the bot with webhook."""
        logger.info(f"Starting Telegram bot with webhook: {webhook_url}")
        self.application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=self.token,
            webhook_url=f"{webhook_url}/{self.token}"
        )
    
    def stop(self):
        """Stop the bot."""
        logger.info("Stopping Telegram bot")
        if self.application:
            self.application.stop()
    
    def run_in_background(self):
        """Run the bot in a background thread."""
        threading.Thread(target=self.start, daemon=True).start()
        logger.info("Telegram bot running in background thread")
