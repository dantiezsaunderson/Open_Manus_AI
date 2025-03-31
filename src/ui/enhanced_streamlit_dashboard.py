"""
Enhanced Streamlit Dashboard Interface

This module provides an improved Streamlit dashboard interface for the Open Manus AI system,
incorporating enhanced conversation, financial analysis, and multi-agent capabilities.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import time
import uuid
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import io
import base64

# Configure page settings
def configure_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Open Manus AI",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/dantiezsaunderson/Open_Manus_AI',
            'Report a bug': 'https://github.com/dantiezsaunderson/Open_Manus_AI/issues',
            'About': "# Open Manus AI\nYour personal AI assistant with advanced capabilities."
        }
    )

# Custom CSS for improved styling
def load_custom_css():
    """Load custom CSS for improved styling."""
    st.markdown("""
    <style>
        /* Main container styling */
        .main {
            background-color: #f5f7f9;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #1e2a38;
        }
        
        /* Header styling */
        h1, h2, h3 {
            color: #1e2a38;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Chat container styling */
        .chat-container {
            border-radius: 10px;
            background-color: white;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        
        /* User message styling */
        .user-message {
            background-color: #e6f7ff;
            border-radius: 15px 15px 0 15px;
            padding: 10px 15px;
            margin: 5px 0;
            max-width: 80%;
            align-self: flex-end;
            float: right;
            clear: both;
        }
        
        /* Assistant message styling */
        .assistant-message {
            background-color: #f0f2f5;
            border-radius: 15px 15px 15px 0;
            padding: 10px 15px;
            margin: 5px 0;
            max-width: 80%;
            align-self: flex-start;
            float: left;
            clear: both;
        }
        
        /* Financial dashboard card styling */
        .dashboard-card {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 15px;
        }
        
        /* Button styling */
        .stButton>button {
            background-color: #1e2a38;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 5px 15px;
            font-weight: 500;
        }
        
        .stButton>button:hover {
            background-color: #2c3e50;
        }
        
        /* Input field styling */
        .stTextInput>div>div>input {
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f0f2f5;
            border-radius: 5px 5px 0 0;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #1e2a38;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    
    if 'conversation_id' not in st.session_state:
        st.session_state.conversation_id = None
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "conversation"
    
    if 'financial_symbols' not in st.session_state:
        st.session_state.financial_symbols = []
    
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []
    
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = []
    
    if 'preferences' not in st.session_state:
        st.session_state.preferences = {
            "theme": "light",
            "communication": {
                "style": "conversational",
                "detail_level": "balanced"
            },
            "topics": {
                "interests": [],
                "dislikes": []
            },
            "financial": {
                "risk_tolerance": "moderate",
                "investment_horizon": "medium-term",
                "preferred_sectors": []
            }
        }
    
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []

# Sidebar navigation
def render_sidebar(conversation_module=None, memory_manager=None):
    """Render the sidebar navigation."""
    st.sidebar.title("Open Manus AI")
    
    # User profile section
    with st.sidebar.expander("User Profile", expanded=False):
        user_name = st.text_input("Your Name", key="user_name")
        if user_name and memory_manager:
            memory_manager.set_preference(st.session_state.user_id, "profile", "name", user_name)
        
        # Theme selection
        theme_options = ["Light", "Dark", "System"]
        selected_theme = st.selectbox(
            "Theme", 
            theme_options, 
            index=theme_options.index(st.session_state.preferences["theme"].capitalize())
        )
        st.session_state.preferences["theme"] = selected_theme.lower()
        
        # Communication preferences
        comm_style_options = ["Conversational", "Concise", "Detailed", "Technical"]
        selected_style = st.selectbox(
            "Communication Style", 
            comm_style_options, 
            index=comm_style_options.index(st.session_state.preferences["communication"]["style"].capitalize())
        )
        st.session_state.preferences["communication"]["style"] = selected_style.lower()
        
        if memory_manager:
            memory_manager.set_preference(
                st.session_state.user_id, 
                "communication", 
                "style", 
                selected_style.lower()
            )
    
    # Navigation
    st.sidebar.header("Navigation")
    
    if st.sidebar.button("💬 Conversation", use_container_width=True):
        st.session_state.current_page = "conversation"
    
    if st.sidebar.button("📊 Financial Dashboard", use_container_width=True):
        st.session_state.current_page = "financial_dashboard"
    
    if st.sidebar.button("🤖 Multi-Agent System", use_container_width=True):
        st.session_state.current_page = "multi_agent"
    
    if st.sidebar.button("⚙️ Settings", use_container_width=True):
        st.session_state.current_page = "settings"
    
    # Conversation history
    if conversation_module and memory_manager:
        st.sidebar.header("Recent Conversations")
        conversations = memory_manager.get_user_conversations(st.session_state.user_id, limit=5)
        
        for conv in conversations:
            conv_title = conv.get("title", "Conversation")
            if st.sidebar.button(f"📝 {conv_title[:25]}...", key=f"conv_{conv['conversation_id']}", use_container_width=True):
                st.session_state.conversation_id = conv["conversation_id"]
                st.session_state.conversation_history = memory_manager.get_conversation_messages(conv["conversation_id"])
                st.session_state.current_page = "conversation"
    
    # Watchlist quick view
    if st.session_state.watchlist:
        st.sidebar.header("Watchlist")
        for symbol in st.session_state.watchlist[:5]:
            st.sidebar.markdown(f"**{symbol}**")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2025 Open Manus AI")
    st.sidebar.markdown("[GitHub Repository](https://github.com/dantiezsaunderson/Open_Manus_AI)")

# Conversation page
def render_conversation_page(conversation_module=None, memory_manager=None, ai_engine=None):
    """Render the conversation page."""
    st.header("💬 Conversation with Open Manus AI")
    
    # Create a new conversation if needed
    if not st.session_state.conversation_id and conversation_module:
        new_conversation = conversation_module.start_conversation(st.session_state.user_id)
        st.session_state.conversation_id = new_conversation["conversation_id"]
    
    # Display conversation suggestions
    if conversation_module:
        suggestions = conversation_module.get_conversation_suggestions(st.session_state.user_id)
        if suggestions:
            with st.expander("Conversation Suggestions", expanded=False):
                cols = st.columns(3)
                for i, suggestion in enumerate(suggestions[:6]):
                    col_idx = i % 3
                    if cols[col_idx].button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                        st.session_state.user_input = suggestion
    
    # Display conversation history
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area
    st.markdown("---")
    user_input = st.text_input("Message Open Manus AI:", key="user_input", placeholder="Type your message here...")
    
    col1, col2, col3 = st.columns([1, 1, 8])
    
    with col1:
        if st.button("Send", use_container_width=True):
            if user_input:
                process_user_message(user_input, conversation_module, memory_manager)
    
    with col2:
        if st.button("New Chat", use_container_width=True):
            if conversation_module:
                new_conversation = conversation_module.start_conversation(st.session_state.user_id)
                st.session_state.conversation_id = new_conversation["conversation_id"]
                st.session_state.conversation_history = []
                st.experimental_rerun()

def process_user_message(user_input, conversation_module=None, memory_manager=None):
    """Process a user message and get a response."""
    if not user_input:
        return
    
    # Add user message to conversation history
    st.session_state.conversation_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    })
    
    # Process message with conversation module
    if conversation_module and st.session_state.conversation_id:
        response = conversation_module.process_message(st.session_state.conversation_id, user_input)
        
        if response.get("success", False) and "response" in response:
            # Add assistant response to conversation history
            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": response["response"],
                "timestamp": datetime.now().isoformat()
            })
    else:
        # Fallback if conversation module is not available
        st.session_state.conversation_history.append({
            "role": "assistant",
            "content": "I'm sorry, the conversation module is not available at the moment.",
            "timestamp": datetime.now().isoformat()
        })
    
    # Clear input
    st.session_state.user_input = ""

# Financial Dashboard page
def render_financial_dashboard(financial_analysis_module=None):
    """Render the financial dashboard page."""
    st.header("📊 Financial Dashboard")
    
    # Tabs for different financial sections
    tab1, tab2, tab3, tab4 = st.tabs(["Market Overview", "Stock Analysis", "Portfolio Tracker", "Watchlist"])
    
    with tab1:
        render_market_overview(financial_analysis_module)
    
    with tab2:
        render_stock_analysis(financial_analysis_module)
    
    with tab3:
        render_portfolio_tracker(financial_analysis_module)
    
    with tab4:
        render_watchlist(financial_analysis_module)

def render_market_overview(financial_analysis_module=None):
    """Render the market overview section."""
    st.subheader("Market Overview")
    
    # Market indices
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("### S&P 500")
        if financial_analysis_module:
            sp500_data = financial_analysis_module.get_stock_data("^GSPC", period="1mo")
            if sp500_data.get("success", False) and "stats" in sp500_data:
                change_pct = sp500_data["stats"]["price_change_pct"]
                color = "green" if change_pct >= 0 else "red"
                st.markdown(f"**Current: ${sp500_data['stats']['latest_price']:.2f}**")
                st.markdown(f"<span style='color:{color};'>**{change_pct:.2f}%**</span>", unsafe_allow_html=True)
            else:
                st.markdown("Data not available")
        else:
            st.markdown("Financial module not available")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("### Dow Jones")
        if financial_analysis_module:
            dow_data = financial_analysis_module.get_stock_data("^DJI", period="1mo")
            if dow_data.get("success", False) and "stats" in dow_data:
                change_pct = dow_data["stats"]["price_change_pct"]
                color = "green" if change_pct >= 0 else "red"
                st.markdown(f"**Current: ${dow_data['stats']['latest_price']:.2f}**")
                st.markdown(f"<span style='color:{color};'>**{change_pct:.2f}%**</span>", unsafe_allow_html=True)
            else:
                st.markdown("Data not available")
        else:
            st.markdown("Financial module not available")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("### NASDAQ")
        if financial_analysis_module:
            nasdaq_data = financial_analysis_module.get_stock_data("^IXIC", period="1mo")
            if nasdaq_data.get("success", False) and "stats" in nasdaq_data:
                change_pct = nasdaq_data["stats"]["price_change_pct"]
                color = "green" if change_pct >= 0 else "red"
                st.markdown(f"**Current: ${nasdaq_data['stats']['latest_price']:.2f}**")
                st.markdown(f"<span style='color:{color};'>**{change_pct:.2f}%**</span>", unsafe_allow_html=True)
            else:
                st.markdown("Data not available")
        else:
            st.markdown("Financial module not available")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Market chart
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### Market Performance (Last Month)")
    
    if financial_analysis_module:
        # Generate chart for S&P 500
        chart_result = financial_analysis_module.generate_stock_chart(
            "^GSPC", 
            period="1mo", 
            chart_type="line",
            include_volume=True,
            include_indicators=True
        )
        
        if chart_result.get("success", False) and "filepath" in chart_result:
            st.image(chart_result["filepath"])
        else:
            st.markdown("Chart not available")
    else:
        st.markdown("Financial module not available")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Top gainers and losers
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("### Top Gainers")
        
        # This would be populated with actual data in a real implementation
        gainers_data = {
            "Symbol": ["AAPL", "MSFT", "AMZN", "GOOGL", "META"],
            "Price": [175.50, 420.30, 180.25, 150.75, 480.20],
            "Change %": [2.5, 1.8, 3.2, 1.5, 4.1]
        }
        
        gainers_df = pd.DataFrame(gainers_data)
        st.dataframe(gainers_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("### Top Losers")
        
        # This would be populated with actual data in a real implementation
        losers_data = {
            "Symbol": ["NFLX", "TSLA", "DIS", "IBM", "INTC"],
            "Price": [550.25, 180.50, 110.30, 140.75, 35.20],
            "Change %": [-1.5, -2.8, -1.2, -0.5, -3.1]
        }
        
        losers_df = pd.DataFrame(losers_data)
        st.dataframe(losers_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_stock_analysis(financial_analysis_module=None):
    """Render the stock analysis section."""
    st.subheader("Stock Analysis")
    
    # Stock search
    col1, col2 = st.columns([3, 1])
    
    with col1:
        stock_symbol = st.text_input("Enter Stock Symbol:", placeholder="e.g., AAPL, MSFT, GOOGL")
    
    with col2:
        analyze_button = st.button("Analyze", use_container_width=True)
    
    if stock_symbol and analyze_button and financial_analysis_module:
        # Perform stock analysis
        analysis_result = financial_analysis_module.analyze_stock(stock_symbol)
        
        if analysis_result.get("success", False):
            # Display stock information
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            
            company_info = analysis_result.get("company_info", {})
            st.markdown(f"### {company_info.get('company_name', stock_symbol)} ({stock_symbol})")
            st.markdown(f"**Exchange:** {company_info.get('exchange', 'Unknown')}")
            st.markdown(f"**Currency:** {company_info.get('currency', 'USD')}")
            
            # Performance metrics
            st.markdown("### Performance")
            performance = analysis_result.get("performance", {})
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if "1d" in performance:
                    change_pct = performance["1d"].get("change_pct", 0)
                    color = "green" if change_pct >= 0 else "red"
                    st.markdown(f"**1 Day:** <span style='color:{color};'>{change_pct:.2f}%</span>", unsafe_allow_html=True)
            
            with col2:
                if "1mo" in performance:
                    change_pct = performance["1mo"].get("change_pct", 0)
                    color = "green" if change_pct >= 0 else "red"
                    st.markdown(f"**1 Month:** <span style='color:{color};'>{change_pct:.2f}%</span>", unsafe_allow_html=True)
            
            with col3:
                if "6mo" in performance:
                    change_pct = performance["6mo"].get("change_pct", 0)
                    color = "green" if change_pct >= 0 else "red"
                    st.markdown(f"**6 Months:** <span style='color:{color};'>{change_pct:.2f}%</span>", unsafe_allow_html=True)
            
            with col4:
                if "1y" in performance:
                    change_pct = performance["1y"].get("change_pct", 0)
                    color = "green" if change_pct >= 0 else "red"
                    st.markdown(f"**1 Year:** <span style='color:{color};'>{change_pct:.2f}%</span>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Stock chart
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.markdown("### Price Chart")
            
            # Chart options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                period = st.selectbox("Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)
            
            with col2:
                chart_type = st.selectbox("Chart Type", ["line", "candle", "ohlc"], index=0)
            
            with col3:
                include_indicators = st.checkbox("Include Indicators", value=True)
            
            # Generate chart
            chart_result = financial_analysis_module.generate_stock_chart(
                stock_symbol, 
                period=period, 
                chart_type=chart_type,
                include_volume=True,
                include_indicators=include_indicators
            )
            
            if chart_result.get("success", False) and "filepath" in chart_result:
                st.image(chart_result["filepath"])
            else:
                st.markdown("Chart not available")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Technical indicators
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.markdown("### Technical Indicators")
            
            technical_indicators = analysis_result.get("technical_indicators", {})
            
            if technical_indicators:
                # Moving averages
                if "moving_averages" in technical_indicators:
                    st.markdown("#### Moving Averages")
                    ma_data = technical_indicators["moving_averages"]
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if "ma20" in ma_data:
                            ma20 = ma_data["ma20"]
                            color = "green" if ma20["signal"] == "bullish" else "red"
                            st.markdown(f"**MA20:** ${ma20['value']:.2f}")
                            st.markdown(f"**Signal:** <span style='color:{color};'>{ma20['signal'].upper()}</span>", unsafe_allow_html=True)
                    
                    with col2:
                        if "ma50" in ma_data:
                            ma50 = ma_data["ma50"]
                            color = "green" if ma50["signal"] == "bullish" else "red"
                            st.markdown(f"**MA50:** ${ma50['value']:.2f}")
                            st.markdown(f"**Signal:** <span style='color:{color};'>{ma50['signal'].upper()}</span>", unsafe_allow_html=True)
                    
                    with col3:
                        if "ma200" in ma_data:
                            ma200 = ma_data["ma200"]
                            color = "green" if ma200["signal"] == "bullish" else "red"
                            st.markdown(f"**MA200:** ${ma200['value']:.2f}")
                            st.markdown(f"**Signal:** <span style='color:{color};'>{ma200['signal'].upper()}</span>", unsafe_allow_html=True)
                
                # RSI
                if "rsi" in technical_indicators:
                    st.markdown("#### Relative Strength Index (RSI)")
                    rsi_data = technical_indicators["rsi"]
                    
                    rsi_value = rsi_data.get("value", 0)
                    rsi_signal = rsi_data.get("signal", "neutral")
                    
                    color = "green"
                    if rsi_signal == "oversold":
                        color = "red"
                    elif rsi_signal == "overbought":
                        color = "orange"
                    
                    st.markdown(f"**RSI Value:** {rsi_value:.2f}")
                    st.markdown(f"**Signal:** <span style='color:{color};'>{rsi_signal.upper()}</span>", unsafe_allow_html=True)
                
                # MACD
                if "macd" in technical_indicators:
                    st.markdown("#### MACD")
                    macd_data = technical_indicators["macd"]
                    
                    macd_value = macd_data.get("macd", 0)
                    signal_value = macd_data.get("signal", 0)
                    histogram = macd_data.get("histogram", 0)
                    trend = macd_data.get("trend", "neutral")
                    
                    color = "green" if trend == "bullish" else "red"
                    
                    st.markdown(f"**MACD:** {macd_value:.4f}")
                    st.markdown(f"**Signal Line:** {signal_value:.4f}")
                    st.markdown(f"**Histogram:** {histogram:.4f}")
                    st.markdown(f"**Trend:** <span style='color:{color};'>{trend.upper()}</span>", unsafe_allow_html=True)
            else:
                st.markdown("Technical indicators not available")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Fundamentals
            if "fundamentals" in analysis_result and analysis_result["fundamentals"].get("success", False):
                st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
                st.markdown("### Fundamental Analysis")
                
                fundamentals = analysis_result["fundamentals"]
                
                # Financial statements
                if "income_statement" in fundamentals:
                    with st.expander("Income Statement", expanded=False):
                        income_statement = fundamentals["income_statement"]
                        if isinstance(income_statement, list) and income_statement:
                            income_df = pd.DataFrame(income_statement)
                            st.dataframe(income_df, use_container_width=True)
                        else:
                            st.markdown("Income statement data not available")
                
                if "balance_sheet" in fundamentals:
                    with st.expander("Balance Sheet", expanded=False):
                        balance_sheet = fundamentals["balance_sheet"]
                        if isinstance(balance_sheet, list) and balance_sheet:
                            balance_df = pd.DataFrame(balance_sheet)
                            st.dataframe(balance_df, use_container_width=True)
                        else:
                            st.markdown("Balance sheet data not available")
                
                # Financial ratios
                if "financial_ratios" in fundamentals:
                    with st.expander("Financial Ratios", expanded=False):
                        ratios = fundamentals["financial_ratios"]
                        if isinstance(ratios, list) and ratios:
                            ratios_df = pd.DataFrame(ratios)
                            st.dataframe(ratios_df, use_container_width=True)
                        else:
                            st.markdown("Financial ratios data not available")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Analyst opinions
            if "analyst_opinions" in analysis_result and analysis_result["analyst_opinions"].get("success", False):
                st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
                st.markdown("### Analyst Opinions")
                
                analyst_opinions = analysis_result["analyst_opinions"]
                
                if "reports" in analyst_opinions:
                    reports = analyst_opinions["reports"]
                    if isinstance(reports, list) and reports:
                        for report in reports[:3]:  # Show top 3 reports
                            st.markdown(f"**{report.get('title', 'Report')}**")
                            st.markdown(f"*{report.get('provider', 'Unknown')} - {report.get('date', 'Unknown date')}*")
                            st.markdown(f"{report.get('abstract', 'No abstract available')}")
                            st.markdown("---")
                    else:
                        st.markdown("No analyst reports available")
                else:
                    st.markdown("Analyst opinions not available")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Add to watchlist/portfolio buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Add to Watchlist", use_container_width=True):
                    if stock_symbol not in st.session_state.watchlist:
                        st.session_state.watchlist.append(stock_symbol)
                        st.success(f"{stock_symbol} added to watchlist!")
                    else:
                        st.info(f"{stock_symbol} is already in your watchlist.")
            
            with col2:
                if st.button("Add to Portfolio", use_container_width=True):
                    # Check if already in portfolio
                    existing_symbols = [item["symbol"] for item in st.session_state.portfolio]
                    if stock_symbol not in existing_symbols:
                        # Show dialog to enter shares and cost basis
                        st.session_state.add_to_portfolio_symbol = stock_symbol
                        st.session_state.add_to_portfolio_dialog = True
                    else:
                        st.info(f"{stock_symbol} is already in your portfolio.")
            
            # Add to portfolio dialog
            if st.session_state.get("add_to_portfolio_dialog", False):
                st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
                st.markdown(f"### Add {st.session_state.add_to_portfolio_symbol} to Portfolio")
                
                shares = st.number_input("Number of Shares", min_value=0.01, step=0.01, value=1.0)
                cost_basis = st.number_input("Cost Basis (per share)", min_value=0.01, step=0.01, value=100.0)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Confirm", use_container_width=True):
                        st.session_state.portfolio.append({
                            "symbol": st.session_state.add_to_portfolio_symbol,
                            "shares": shares,
                            "cost_basis": cost_basis,
                            "date_added": datetime.now().isoformat()
                        })
                        st.success(f"{st.session_state.add_to_portfolio_symbol} added to portfolio!")
                        st.session_state.add_to_portfolio_dialog = False
                        st.session_state.add_to_portfolio_symbol = None
                
                with col2:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state.add_to_portfolio_dialog = False
                        st.session_state.add_to_portfolio_symbol = None
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error(f"Error analyzing {stock_symbol}: {analysis_result.get('error', 'Unknown error')}")

def render_portfolio_tracker(financial_analysis_module=None):
    """Render the portfolio tracker section."""
    st.subheader("Portfolio Tracker")
    
    # Portfolio summary
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    
    if not st.session_state.portfolio:
        st.markdown("### Your Portfolio is Empty")
        st.markdown("Add stocks to your portfolio from the Stock Analysis tab.")
    else:
        st.markdown("### Portfolio Summary")
        
        # Analyze portfolio
        if financial_analysis_module:
            portfolio_analysis = financial_analysis_module.analyze_portfolio(st.session_state.portfolio)
            
            if portfolio_analysis.get("success", False):
                # Display portfolio value and performance
                total_value = portfolio_analysis.get("total_value", 0)
                total_cost = portfolio_analysis.get("total_cost", 0)
                gain_loss = portfolio_analysis.get("gain_loss", 0)
                gain_loss_pct = portfolio_analysis.get("gain_loss_pct", 0)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Value", f"${total_value:.2f}")
                
                with col2:
                    st.metric("Total Cost", f"${total_cost:.2f}")
                
                with col3:
                    color = "green" if gain_loss >= 0 else "red"
                    st.markdown(f"**Gain/Loss:** <span style='color:{color};'>${gain_loss:.2f} ({gain_loss_pct:.2f}%)</span>", unsafe_allow_html=True)
                
                # Portfolio holdings table
                st.markdown("### Holdings")
                
                holdings_data = []
                for holding in portfolio_analysis.get("holdings", []):
                    if holding.get("success", False):
                        holdings_data.append({
                            "Symbol": holding["symbol"],
                            "Company": holding.get("company_name", holding["symbol"]),
                            "Shares": holding["shares"],
                            "Current Price": f"${holding['latest_price']:.2f}",
                            "Current Value": f"${holding['current_value']:.2f}",
                            "Cost Basis": f"${holding['cost_basis']:.2f}",
                            "Gain/Loss %": f"{holding['gain_loss_pct']:.2f}%"
                        })
                
                if holdings_data:
                    holdings_df = pd.DataFrame(holdings_data)
                    st.dataframe(holdings_df, use_container_width=True)
                else:
                    st.markdown("No holdings data available")
                
                # Portfolio allocation chart
                st.markdown("### Portfolio Allocation")
                
                # Create allocation data
                allocation_data = []
                for holding in portfolio_analysis.get("holdings", []):
                    if holding.get("success", False):
                        allocation_data.append({
                            "Symbol": holding["symbol"],
                            "Value": holding["current_value"]
                        })
                
                if allocation_data:
                    allocation_df = pd.DataFrame(allocation_data)
                    
                    # Create pie chart
                    fig = px.pie(
                        allocation_df, 
                        values="Value", 
                        names="Symbol", 
                        title="Portfolio Allocation by Value",
                        hole=0.4
                    )
                    fig.update_layout(
                        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.markdown("No allocation data available")
            else:
                st.error(f"Error analyzing portfolio: {portfolio_analysis.get('error', 'Unknown error')}")
        else:
            # Display basic portfolio without analysis
            st.markdown("### Holdings")
            
            holdings_data = []
            for holding in st.session_state.portfolio:
                holdings_data.append({
                    "Symbol": holding["symbol"],
                    "Shares": holding["shares"],
                    "Cost Basis": f"${holding['cost_basis']:.2f}",
                    "Date Added": holding["date_added"].split("T")[0] if "T" in holding["date_added"] else holding["date_added"]
                })
            
            if holdings_data:
                holdings_df = pd.DataFrame(holdings_data)
                st.dataframe(holdings_df, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add new holding manually
    with st.expander("Add New Holding", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_symbol = st.text_input("Symbol", placeholder="e.g., AAPL")
        
        with col2:
            new_shares = st.number_input("Number of Shares", min_value=0.01, step=0.01, value=1.0)
        
        with col3:
            new_cost_basis = st.number_input("Cost Basis (per share)", min_value=0.01, step=0.01, value=100.0)
        
        if st.button("Add to Portfolio", use_container_width=True):
            if new_symbol:
                # Check if already in portfolio
                existing_symbols = [item["symbol"] for item in st.session_state.portfolio]
                if new_symbol not in existing_symbols:
                    st.session_state.portfolio.append({
                        "symbol": new_symbol,
                        "shares": new_shares,
                        "cost_basis": new_cost_basis,
                        "date_added": datetime.now().isoformat()
                    })
                    st.success(f"{new_symbol} added to portfolio!")
                    st.experimental_rerun()
                else:
                    st.info(f"{new_symbol} is already in your portfolio.")
            else:
                st.warning("Please enter a symbol.")

def render_watchlist(financial_analysis_module=None):
    """Render the watchlist section."""
    st.subheader("Watchlist")
    
    # Watchlist table
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    
    if not st.session_state.watchlist:
        st.markdown("### Your Watchlist is Empty")
        st.markdown("Add stocks to your watchlist from the Stock Analysis tab.")
    else:
        st.markdown("### Watchlist")
        
        # Get data for watchlist symbols
        watchlist_data = []
        
        if financial_analysis_module:
            for symbol in st.session_state.watchlist:
                stock_data = financial_analysis_module.get_stock_data(symbol, period="1d")
                
                if stock_data.get("success", False) and "stats" in stock_data:
                    watchlist_data.append({
                        "Symbol": symbol,
                        "Company": stock_data.get("company_name", symbol),
                        "Price": f"${stock_data['stats']['latest_price']:.2f}",
                        "Change": f"{stock_data['stats']['price_change']:.2f}",
                        "Change %": f"{stock_data['stats']['price_change_pct']:.2f}%",
                        "Volume": stock_data['stats'].get('avg_volume', 'N/A')
                    })
                else:
                    watchlist_data.append({
                        "Symbol": symbol,
                        "Company": symbol,
                        "Price": "N/A",
                        "Change": "N/A",
                        "Change %": "N/A",
                        "Volume": "N/A"
                    })
        else:
            # Basic watchlist without data
            for symbol in st.session_state.watchlist:
                watchlist_data.append({
                    "Symbol": symbol,
                    "Company": symbol,
                    "Price": "N/A",
                    "Change": "N/A",
                    "Change %": "N/A",
                    "Volume": "N/A"
                })
        
        if watchlist_data:
            watchlist_df = pd.DataFrame(watchlist_data)
            st.dataframe(watchlist_df, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add to watchlist
    with st.expander("Add to Watchlist", expanded=False):
        new_symbol = st.text_input("Symbol", placeholder="e.g., AAPL")
        
        if st.button("Add", use_container_width=True):
            if new_symbol:
                if new_symbol not in st.session_state.watchlist:
                    st.session_state.watchlist.append(new_symbol)
                    st.success(f"{new_symbol} added to watchlist!")
                    st.experimental_rerun()
                else:
                    st.info(f"{new_symbol} is already in your watchlist.")
            else:
                st.warning("Please enter a symbol.")
    
    # Remove from watchlist
    if st.session_state.watchlist:
        with st.expander("Remove from Watchlist", expanded=False):
            symbol_to_remove = st.selectbox("Select Symbol", st.session_state.watchlist)
            
            if st.button("Remove", use_container_width=True):
                if symbol_to_remove in st.session_state.watchlist:
                    st.session_state.watchlist.remove(symbol_to_remove)
                    st.success(f"{symbol_to_remove} removed from watchlist!")
                    st.experimental_rerun()

# Multi-Agent System page
def render_multi_agent_page(multi_agent_system=None):
    """Render the multi-agent system page."""
    st.header("🤖 Multi-Agent System")
    
    if not multi_agent_system:
        st.warning("Multi-agent system is not available.")
        return
    
    # System status
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### System Status")
    
    system_status = multi_agent_system.get_system_status()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Active Agents", system_status.get("agent_count", 0))
    
    with col2:
        st.metric("Active Tasks", system_status.get("active_tasks", 0))
    
    # Agent status table
    agent_data = []
    for agent in system_status.get("agents", []):
        agent_data.append({
            "Name": agent.get("name", "Unknown"),
            "Type": agent.get("type", "Unknown"),
            "Status": agent.get("status", "Unknown"),
            "Queue Size": agent.get("queue_size", 0),
            "Active Tasks": agent.get("active_tasks", 0)
        })
    
    if agent_data:
        agent_df = pd.DataFrame(agent_data)
        st.dataframe(agent_df, use_container_width=True)
    else:
        st.markdown("No agents available")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Task submission
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### Submit Task")
    
    # Task type selection
    task_type = st.selectbox(
        "Task Type", 
        [
            "Research", 
            "Code Generation", 
            "Code Analysis", 
            "Stock Analysis", 
            "Technical Analysis",
            "Fundamental Analysis",
            "Portfolio Analysis",
            "Stock Screening"
        ]
    )
    
    # Task parameters based on type
    if task_type in ["Stock Analysis", "Technical Analysis", "Fundamental Analysis"]:
        symbol = st.text_input("Stock Symbol", placeholder="e.g., AAPL")
        
        if task_type == "Technical Analysis":
            period = st.selectbox("Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y"], index=2)
            indicators = st.multiselect(
                "Indicators", 
                ["SMA", "EMA", "RSI", "MACD", "Bollinger Bands"], 
                default=["SMA", "RSI", "MACD"]
            )
            
            task_params = {
                "task_type": "analyze",
                "symbol": symbol,
                "period": period,
                "indicators": indicators
            }
        elif task_type == "Fundamental Analysis":
            task_params = {
                "task_type": "analyze",
                "symbol": symbol
            }
        else:
            task_params = {
                "task_type": "analyze_stock",
                "symbol": symbol
            }
    elif task_type == "Portfolio Analysis":
        task_params = {
            "task_type": "analyze_portfolio",
            "portfolio": st.session_state.portfolio
        }
    elif task_type == "Stock Screening":
        min_price = st.number_input("Minimum Price", value=0.0, step=1.0)
        max_price = st.number_input("Maximum Price", value=1000.0, step=10.0)
        min_performance = st.number_input("Minimum Performance (%)", value=0.0, step=1.0)
        
        symbols = st.text_input("Symbols to Screen (comma-separated)", placeholder="e.g., AAPL,MSFT,GOOGL")
        symbol_list = [s.strip() for s in symbols.split(",")] if symbols else []
        
        task_params = {
            "task_type": "screen",
            "criteria": {
                "min_price": min_price,
                "max_price": max_price,
                "min_performance": min_performance,
                "performance_period": "1mo"
            },
            "symbols": symbol_list
        }
    elif task_type == "Research":
        query = st.text_area("Research Query", placeholder="Enter your research question or topic")
        task_params = {
            "task_type": "general",
            "query": query
        }
    elif task_type == "Code Generation":
        language = st.selectbox("Programming Language", ["python", "javascript", "java", "c++", "go", "rust"])
        prompt = st.text_area("Code Requirements", placeholder="Describe what you want the code to do")
        task_params = {
            "task_type": "generate",
            "language": language,
            "prompt": prompt
        }
    elif task_type == "Code Analysis":
        language = st.selectbox("Programming Language", ["python", "javascript", "java", "c++", "go", "rust"])
        code = st.text_area("Code to Analyze", placeholder="Paste your code here")
        task_params = {
            "task_type": "analyze",
            "language": language,
            "code": code
        }
    
    # Submit button
    if st.button("Submit Task", use_container_width=True):
        # Determine agent type based on task
        agent_type = None
        if task_type == "Research":
            agent_type = "research"
        elif task_type in ["Code Generation", "Code Analysis"]:
            agent_type = "coding"
        elif task_type == "Stock Analysis":
            agent_type = "financial"
        elif task_type == "Technical Analysis":
            agent_type = "technical_analysis"
        elif task_type == "Fundamental Analysis":
            agent_type = "fundamental_analysis"
        elif task_type == "Stock Screening":
            agent_type = "stock_screener"
        
        # Submit task
        task_id = multi_agent_system.assign_task(task_params, agent_type=agent_type)
        
        if task_id:
            st.success(f"Task submitted successfully! Task ID: {task_id}")
            st.session_state.last_task_id = task_id
        else:
            st.error("Failed to submit task.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Task results
    if hasattr(st.session_state, "last_task_id"):
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("### Task Results")
        
        task_id = st.session_state.last_task_id
        task_result = multi_agent_system.get_task_result(task_id)
        
        st.markdown(f"**Task ID:** {task_id}")
        st.markdown(f"**Status:** {task_result.get('status', 'Unknown')}")
        
        if task_result.get("status") == "completed":
            st.markdown("**Result:**")
            
            result = task_result.get("result", {})
            
            # Display result based on task type
            if "analysis" in result:
                st.json(result["analysis"])
            elif "code" in result:
                st.code(result["code"])
            elif "research" in result:
                st.markdown(result["research"])
            elif "summary" in result:
                st.markdown(result["summary"])
            elif "matches" in result:
                st.markdown(f"**Found {result.get('total_matches', 0)} matches out of {result.get('total_screened', 0)} stocks**")
                
                matches = result.get("matches", [])
                for match in matches:
                    st.markdown(f"**{match['symbol']}**")
                    st.json(match)
            else:
                st.json(result)
        elif task_result.get("status") == "processing":
            st.markdown(f"**Progress:** {task_result.get('progress', 0)}%")
            st.markdown(f"**Status Message:** {task_result.get('status_message', 'Processing...')}")
            
            # Auto-refresh
            st.markdown("Refreshing results in 5 seconds...")
            st.experimental_rerun()
        elif task_result.get("status") == "failed":
            st.error(f"Task failed: {task_result.get('error', 'Unknown error')}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Settings page
def render_settings_page(memory_manager=None):
    """Render the settings page."""
    st.header("⚙️ Settings")
    
    # User preferences
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### User Preferences")
    
    # General preferences
    st.markdown("#### General")
    
    theme_options = ["Light", "Dark", "System"]
    selected_theme = st.selectbox(
        "Theme", 
        theme_options, 
        index=theme_options.index(st.session_state.preferences["theme"].capitalize())
    )
    st.session_state.preferences["theme"] = selected_theme.lower()
    
    # Communication preferences
    st.markdown("#### Communication")
    
    comm_style_options = ["Conversational", "Concise", "Detailed", "Technical"]
    selected_style = st.selectbox(
        "Communication Style", 
        comm_style_options, 
        index=comm_style_options.index(st.session_state.preferences["communication"]["style"].capitalize())
    )
    st.session_state.preferences["communication"]["style"] = selected_style.lower()
    
    detail_level_options = ["Minimal", "Balanced", "Comprehensive"]
    selected_detail = st.selectbox(
        "Detail Level", 
        detail_level_options, 
        index=detail_level_options.index(st.session_state.preferences["communication"]["detail_level"].capitalize())
    )
    st.session_state.preferences["communication"]["detail_level"] = selected_detail.lower()
    
    # Topics preferences
    st.markdown("#### Topics")
    
    interests = st.text_input(
        "Interests (comma-separated)", 
        value=",".join(st.session_state.preferences["topics"]["interests"])
    )
    st.session_state.preferences["topics"]["interests"] = [i.strip() for i in interests.split(",") if i.strip()]
    
    dislikes = st.text_input(
        "Dislikes (comma-separated)", 
        value=",".join(st.session_state.preferences["topics"]["dislikes"])
    )
    st.session_state.preferences["topics"]["dislikes"] = [d.strip() for d in dislikes.split(",") if d.strip()]
    
    # Financial preferences
    st.markdown("#### Financial")
    
    risk_options = ["Conservative", "Moderate", "Aggressive"]
    selected_risk = st.selectbox(
        "Risk Tolerance", 
        risk_options, 
        index=risk_options.index(st.session_state.preferences["financial"]["risk_tolerance"].capitalize())
    )
    st.session_state.preferences["financial"]["risk_tolerance"] = selected_risk.lower()
    
    horizon_options = ["Short-term", "Medium-term", "Long-term"]
    selected_horizon = st.selectbox(
        "Investment Horizon", 
        horizon_options, 
        index=horizon_options.index(st.session_state.preferences["financial"]["investment_horizon"].capitalize())
    )
    st.session_state.preferences["financial"]["investment_horizon"] = selected_horizon.lower()
    
    sectors = st.text_input(
        "Preferred Sectors (comma-separated)", 
        value=",".join(st.session_state.preferences["financial"]["preferred_sectors"])
    )
    st.session_state.preferences["financial"]["preferred_sectors"] = [s.strip() for s in sectors.split(",") if s.strip()]
    
    # Save preferences
    if st.button("Save Preferences", use_container_width=True):
        if memory_manager:
            # Save to memory manager
            for category, prefs in st.session_state.preferences.items():
                if isinstance(prefs, dict):
                    for key, value in prefs.items():
                        memory_manager.set_preference(st.session_state.user_id, category, key, value)
                else:
                    memory_manager.set_preference(st.session_state.user_id, "general", category, prefs)
            
            st.success("Preferences saved successfully!")
        else:
            st.warning("Memory manager not available. Preferences saved to session only.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Data management
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export User Data", use_container_width=True):
            if memory_manager:
                user_data = memory_manager.export_user_data(st.session_state.user_id)
                
                # Convert to JSON
                user_data_json = json.dumps(user_data, indent=2)
                
                # Create download link
                b64 = base64.b64encode(user_data_json.encode()).decode()
                href = f'<a href="data:application/json;base64,{b64}" download="open_manus_user_data.json">Download User Data</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.warning("Memory manager not available.")
    
    with col2:
        if st.button("Clear User Data", use_container_width=True):
            if memory_manager:
                # Show confirmation
                st.session_state.show_clear_confirmation = True
            else:
                st.warning("Memory manager not available.")
    
    # Clear data confirmation
    if st.session_state.get("show_clear_confirmation", False):
        st.warning("Are you sure you want to clear all your data? This action cannot be undone.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Yes, Clear My Data", use_container_width=True):
                if memory_manager:
                    success = memory_manager.clear_user_data(st.session_state.user_id)
                    if success:
                        st.success("Your data has been cleared successfully.")
                        
                        # Reset session state
                        st.session_state.conversation_id = None
                        st.session_state.conversation_history = []
                        st.session_state.portfolio = []
                        st.session_state.watchlist = []
                        
                        st.session_state.show_clear_confirmation = False
                        st.experimental_rerun()
                    else:
                        st.error("Failed to clear your data. Please try again.")
                else:
                    st.warning("Memory manager not available.")
        
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_clear_confirmation = False
                st.experimental_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # API configuration
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### API Configuration")
    
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    financialdata_api_key = st.text_input("FinancialData.net API Key", type="password")
    
    if st.button("Save API Keys", use_container_width=True):
        if memory_manager:
            if openai_api_key:
                memory_manager.set_preference(st.session_state.user_id, "api_keys", "openai", openai_api_key)
            
            if financialdata_api_key:
                memory_manager.set_preference(st.session_state.user_id, "api_keys", "financialdata", financialdata_api_key)
            
            st.success("API keys saved successfully!")
        else:
            st.warning("Memory manager not available. API keys not saved.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main application
def main(ai_engine=None, memory_manager=None, conversation_module=None, financial_analysis_module=None, multi_agent_system=None):
    """Main application entry point."""
    # Configure page
    configure_page()
    
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar(conversation_module, memory_manager)
    
    # Render current page
    if st.session_state.current_page == "conversation":
        render_conversation_page(conversation_module, memory_manager, ai_engine)
    elif st.session_state.current_page == "financial_dashboard":
        render_financial_dashboard(financial_analysis_module)
    elif st.session_state.current_page == "multi_agent":
        render_multi_agent_page(multi_agent_system)
    elif st.session_state.current_page == "settings":
        render_settings_page(memory_manager)

if __name__ == "__main__":
    main()
