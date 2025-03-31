"""
Streamlit Dashboard for Open Manus AI

This module implements a web-based dashboard using Streamlit for the Open Manus AI system.
"""

import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime, timedelta
import json
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

# Configure page
st.set_page_config(
    page_title="Open Manus AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.conversation_history = []
    st.session_state.current_user = "default_user"
    st.session_state.current_tab = "conversation"
    st.session_state.stock_data = None
    st.session_state.weather_data = None
    st.session_state.news_data = None
    st.session_state.code_output = None

# Function to initialize components
@st.cache_resource
def initialize_components():
    """Initialize all Open Manus AI components."""
    # Initialize core components
    memory_manager = MemoryManager()
    ai_engine = AIEngine()
    
    # Initialize modules
    conversation_module = ConversationModule(ai_engine, memory_manager)
    task_automation = TaskAutomationModule(ai_engine, memory_manager)
    coding_support = CodingSupportModule(ai_engine)
    financial_analysis = FinancialAnalysisModule()
    multi_agent_system = MultiAgentSystem(ai_engine)
    
    # Initialize API integrations
    openai_api = OpenAIAPI()
    financial_api = FinancialDataAPI()
    weather_api = WeatherAPI()
    news_api = NewsAPI()
    
    components = {
        "ai_engine": ai_engine,
        "memory_manager": memory_manager,
        "conversation": conversation_module,
        "task_automation": task_automation,
        "coding_support": coding_support,
        "financial_analysis": financial_analysis,
        "multi_agent": multi_agent_system,
        "openai_api": openai_api,
        "financial_api": financial_api,
        "weather_api": weather_api,
        "news_api": news_api
    }
    
    return components

# Initialize components
components = initialize_components()
st.session_state.initialized = True

# Sidebar
with st.sidebar:
    st.title("Open Manus AI")
    st.image("https://raw.githubusercontent.com/dantiezsaunderson/Open_Manus_AI/main/docs/logo.png", width=100)
    
    # User selection
    st.subheader("User")
    user_id = st.text_input("User ID", value=st.session_state.current_user)
    if user_id != st.session_state.current_user:
        st.session_state.current_user = user_id
        st.session_state.conversation_history = []
    
    # Navigation
    st.subheader("Navigation")
    tabs = {
        "conversation": "💬 Conversation",
        "financial": "📈 Financial Analysis",
        "coding": "💻 Coding Support",
        "weather": "🌤️ Weather",
        "news": "📰 News",
        "settings": "⚙️ Settings"
    }
    
    for tab_id, tab_name in tabs.items():
        if st.button(tab_name, key=f"tab_{tab_id}"):
            st.session_state.current_tab = tab_id
    
    # About section
    st.subheader("About")
    st.markdown("""
    **Open Manus AI** is an open-source personal AI assistant with advanced capabilities.
    
    [GitHub Repository](https://github.com/dantiezsaunderson/Open_Manus_AI)
    """)

# Main content area
st.title("Open Manus AI")

# Conversation tab
if st.session_state.current_tab == "conversation":
    st.header("💬 Conversation")
    
    # Display conversation history
    for i, message in enumerate(st.session_state.conversation_history):
        if i % 2 == 0:  # User message
            st.markdown(f"**You:** {message}")
        else:  # AI response
            st.markdown(f"**Open Manus AI:** {message}")
    
    # Input for new message
    user_input = st.text_area("Your message:", height=100)
    
    if st.button("Send"):
        if user_input:
            # Add user message to history
            st.session_state.conversation_history.append(user_input)
            
            # Get AI response
            with st.spinner("Thinking..."):
                response = components["conversation"].get_response(
                    st.session_state.current_user, 
                    user_input
                )
            
            # Add AI response to history
            st.session_state.conversation_history.append(response)
            
            # Clear input
            st.experimental_rerun()

# Financial Analysis tab
elif st.session_state.current_tab == "financial":
    st.header("📈 Financial Analysis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Stock Lookup")
        symbol = st.text_input("Enter stock symbol:", value="AAPL")
        period = st.selectbox("Time period:", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])
        
        if st.button("Get Stock Data"):
            with st.spinner("Fetching stock data..."):
                stock_data = components["financial_analysis"].get_stock_data(symbol, period=period)
                st.session_state.stock_data = stock_data
    
    with col2:
        if st.session_state.stock_data:
            if st.session_state.stock_data.get('success', False):
                st.subheader(f"{st.session_state.stock_data['company_name']} ({st.session_state.stock_data['symbol']})")
                
                # Display stock info
                st.markdown(f"**Sector:** {st.session_state.stock_data.get('sector', 'N/A')}")
                st.markdown(f"**Industry:** {st.session_state.stock_data.get('industry', 'N/A')}")
                st.markdown(f"**Market Cap:** {st.session_state.stock_data.get('market_cap', 'N/A')}")
                
                # Display stock chart
                if st.button("Generate Chart"):
                    with st.spinner("Generating chart..."):
                        chart_result = components["financial_analysis"].generate_stock_chart(
                            symbol, 
                            period=period,
                            output_dir="/tmp"
                        )
                        
                        if chart_result.get('success', False):
                            st.image(chart_result['filepath'])
                        else:
                            st.error(f"Error generating chart: {chart_result.get('error', 'Unknown error')}")
                
                # Display stock analysis
                if st.button("Analyze Stock"):
                    with st.spinner("Analyzing stock..."):
                        analysis = components["financial_analysis"].analyze_stock(symbol)
                        
                        if analysis.get('success', False):
                            # Performance
                            st.subheader("Performance")
                            performance = analysis.get('performance', {})
                            
                            perf_data = []
                            for period, data in performance.items():
                                perf_data.append({
                                    "Period": period,
                                    "Change": f"{data.get('change', 0):.2f}",
                                    "Change %": f"{data.get('change_pct', 0):.2f}%"
                                })
                            
                            if perf_data:
                                st.table(pd.DataFrame(perf_data))
                            
                            # Technical Indicators
                            st.subheader("Technical Indicators")
                            indicators = analysis.get('technical_indicators', {})
                            
                            if indicators:
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown(f"**Price:** ${indicators.get('price', 0):.2f}")
                                    st.markdown(f"**MA20:** ${indicators.get('ma20', 0):.2f}")
                                    st.markdown(f"**MA50:** ${indicators.get('ma50', 0):.2f}")
                                
                                with col2:
                                    st.markdown(f"**RSI:** {indicators.get('rsi', 0):.2f}")
                                    st.markdown(f"**MACD:** {indicators.get('macd', 0):.2f}")
                                    st.markdown(f"**Signal:** {indicators.get('macd_signal', 0):.2f}")
                                
                                # Signals
                                st.subheader("Signals")
                                signals = []
                                
                                if indicators.get('above_ma20', False):
                                    signals.append("✅ Price above 20-day moving average")
                                else:
                                    signals.append("❌ Price below 20-day moving average")
                                    
                                if indicators.get('above_ma50', False):
                                    signals.append("✅ Price above 50-day moving average")
                                else:
                                    signals.append("❌ Price below 50-day moving average")
                                    
                                if indicators.get('rsi_oversold', False):
                                    signals.append("⚠️ RSI indicates oversold conditions")
                                elif indicators.get('rsi_overbought', False):
                                    signals.append("⚠️ RSI indicates overbought conditions")
                                else:
                                    signals.append("✅ RSI in neutral range")
                                    
                                if indicators.get('macd_bullish', False):
                                    signals.append("✅ MACD indicates bullish trend")
                                else:
                                    signals.append("❌ MACD indicates bearish trend")
                                
                                for signal in signals:
                                    st.markdown(signal)
                        else:
                            st.error(f"Error analyzing stock: {analysis.get('error', 'Unknown error')}")
            else:
                st.error(f"Error: {st.session_state.stock_data.get('error', 'Unknown error')}")
        else:
            st.info("Enter a stock symbol and click 'Get Stock Data' to begin.")
    
    # Market Overview
    st.subheader("Market Overview")
    if st.button("Get Market Overview"):
        with st.spinner("Fetching market data..."):
            market_data = components["financial_analysis"].get_market_overview()
            
            if market_data.get('success', False):
                market_indices = market_data.get('data', {})
                
                if market_indices:
                    index_data = []
                    for symbol, data in market_indices.items():
                        index_data.append({
                            "Index": data.get('name', symbol),
                            "Price": f"{data.get('latest_price', 0):.2f}",
                            "Change": f"{data.get('change', 0):.2f}",
                            "Change %": f"{data.get('change_pct', 0):.2f}%"
                        })
                    
                    st.table(pd.DataFrame(index_data))
                else:
                    st.warning("No market data available.")
            else:
                st.error(f"Error: {market_data.get('error', 'Unknown error')}")

# Coding Support tab
elif st.session_state.current_tab == "coding":
    st.header("💻 Coding Support")
    
    coding_tabs = st.tabs(["Generate Code", "Analyze Code", "Execute Code"])
    
    # Generate Code tab
    with coding_tabs[0]:
        st.subheader("Generate Code")
        
        prompt = st.text_area("Describe what you want to create:", height=150)
        language = st.selectbox("Programming language:", ["python", "javascript", "java", "c++", "go", "rust", "html", "css", "sql"])
        detailed = st.checkbox("Include detailed comments and explanations", value=True)
        
        if st.button("Generate Code"):
            if prompt:
                with st.spinner("Generating code..."):
                    result = components["coding_support"].generate_code(prompt, language, detailed)
                    
                    if result.get('success', False):
                        st.code(result['code'], language=language)
                        
                        with st.expander("Explanation"):
                            st.markdown(result['explanation'])
                    else:
                        st.error(f"Error: {result.get('explanation', 'Unknown error')}")
            else:
                st.warning("Please enter a description of the code you want to generate.")
    
    # Analyze Code tab
    with coding_tabs[1]:
        st.subheader("Analyze Code")
        
        code_to_analyze = st.text_area("Enter code to analyze:", height=300)
        analyze_language = st.selectbox("Language:", ["python", "javascript", "java", "c++", "go", "rust", "html", "css", "sql"], key="analyze_language")
        
        if st.button("Analyze Code"):
            if code_to_analyze:
                with st.spinner("Analyzing code..."):
                    result = components["coding_support"].analyze_code(code_to_analyze, analyze_language)
                    
                    if result.get('success', False):
                        st.markdown("### Analysis Results")
                        st.markdown(result['analysis'])
                    else:
                        st.error(f"Error: {result.get('analysis', 'Unknown error')}")
            else:
                st.warning("Please enter code to analyze.")
    
    # Execute Code tab
    with coding_tabs[2]:
        st.subheader("Execute Code")
        st.warning("⚠️ This feature executes code in a sandbox environment. Use responsibly.")
        
        code_to_execute = st.text_area("Enter Python code to execute:", height=300)
        timeout = st.slider("Execution timeout (seconds):", min_value=1, max_value=60, value=10)
        
        if st.button("Execute Code"):
            if code_to_execute:
                with st.spinner("Executing code..."):
                    result = components["coding_support"].execute_code(code_to_execute, timeout=timeout)
                    st.session_state.code_output = result
            else:
                st.warning("Please enter code to execute.")
        
        if st.session_state.code_output:
            st.markdown("### Execution Results")
            
            if st.session_state.code_output.get('success', False):
                st.markdown("✅ **Code executed successfully**")
                
                if st.session_state.code_output.get('output'):
                    st.markdown("**Output:**")
                    st.code(st.session_state.code_output['output'])
                else:
                    st.info("No output produced.")
            else:
                st.markdown("❌ **Execution failed**")
                
                if st.session_state.code_output.get('error'):
                    st.markdown("**Error:**")
                    st.code(st.session_state.code_output['error'])

# Weather tab
elif st.session_state.current_tab == "weather":
    st.header("🌤️ Weather")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Weather Lookup")
        location = st.text_input("Enter location (city or coordinates):", value="New York")
        units = st.selectbox("Units:", ["metric", "imperial"])
        
        if st.button("Get Weather"):
            with st.spinner("Fetching weather data..."):
                weather_api = components["weather_api"]
                current_weather = weather_api.get_current_weather(location, units)
                forecast = weather_api.get_weather_forecast(location, units)
                
                st.session_state.weather_data = {
                    "current": current_weather,
                    "forecast": forecast
                }
    
    with col2:
        if st.session_state.weather_data:
            current = st.session_state.weather_data["current"]
            forecast = st.session_state.weather_data["forecast"]
            
            if current.get('success', False):
                weather_data = current.get('weather_data', {})
                
                # Display current weather
                st.subheader(f"Current Weather in {weather_data.get('location', {}).get('name', location)}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    temp = weather_data.get('weather', {}).get('temperature', {}).get('current', 0)
                    feels_like = weather_data.get('weather', {}).get('temperature', {}).get('feels_like', 0)
                    
                    if units == "metric":
                        st.markdown(f"### {temp}°C")
                        st.markdown(f"Feels like: {feels_like}°C")
                    else:
                        st.markdown(f"### {temp}°F")
                        st.markdown(f"Feels like: {feels_like}°F")
                
                with col2:
                    condition = weather_data.get('weather', {}).get('condition', '')
                    description = weather_data.get('weather', {}).get('description', '')
                    st.markdown(f"### {condition}")
                    st.markdown(description.capitalize())
                
                with col3:
                    humidity = weather_data.get('weather', {}).get('humidity', 0)
                    wind_speed = weather_data.get('weather', {}).get('wind', {}).get('speed', 0)
                    
                    st.markdown(f"Humidity: {humidity}%")
                    
                    if units == "metric":
                        st.markdown(f"Wind: {wind_speed} m/s")
                    else:
                        st.markdown(f"Wind: {wind_speed} mph")
            else:
                st.error(f"Error: {current.get('error', 'Unknown error')}")
            
            # Display forecast
            if forecast.get('success', False):
                st.subheader("5-Day Forecast")
                
                forecast_data = forecast.get('forecast_data', {})
                forecast_days = forecast_data.get('forecast', {})
                
                if forecast_days:
                    cols = st.columns(min(len(forecast_days), 5))
                    
                    for i, (date, day_data) in enumerate(list(forecast_days.items())[:5]):
                        with cols[i]:
                            # Get mid-day forecast (around noon)
                            mid_day = None
                            for item in day_data:
                                item_time = datetime.fromisoformat(item['datetime'])
                                if 11 <= item_time.hour <= 14:
                                    mid_day = item
                                    break
                            
                            if not mid_day and day_data:
                                mid_day = day_data[len(day_data)//2]  # Use middle of the day if noon not found
                            
                            if mid_day:
                                # Format date
                                day_date = datetime.fromisoformat(mid_day['datetime']).strftime("%a, %b %d")
                                st.markdown(f"**{day_date}**")
                                
                                # Temperature
                                temp = mid_day.get('temperature', {}).get('current', 0)
                                if units == "metric":
                                    st.markdown(f"{temp}°C")
                                else:
                                    st.markdown(f"{temp}°F")
                                
                                # Weather condition
                                condition = mid_day.get('weather', {}).get('condition', '')
                                st.markdown(condition)
                                
                                # Precipitation probability
                                pop = mid_day.get('precipitation', {}).get('probability', 0) * 100
                                st.markdown(f"Rain: {pop:.0f}%")
                else:
                    st.warning("No forecast data available.")
            else:
                st.error(f"Error: {forecast.get('error', 'Unknown error')}")
        else:
            st.info("Enter a location and click 'Get Weather' to begin.")
    
    # Air Quality
    if st.session_state.weather_data and st.session_state.weather_data["current"].get('success', False):
        st.subheader("Air Quality")
        
        weather_data = st.session_state.weather_data["current"].get('weather_data', {})
        coordinates = weather_data.get('location', {}).get('coordinates', {})
        
        if coordinates:
            lat = coordinates.get('lat')
            lon = coordinates.get('lon')
            
            if lat and lon:
                coord_str = f"{lat},{lon}"
                
                if st.button("Check Air Quality"):
                    with st.spinner("Fetching air quality data..."):
                        air_quality = components["weather_api"].get_air_pollution(coord_str)
                        
                        if air_quality.get('success', False):
                            pollution_data = air_quality.get('pollution_data', {})
                            
                            # Display AQI
                            aqi = pollution_data.get('air_quality', {}).get('aqi', 0)
                            description = pollution_data.get('air_quality', {}).get('description', '')
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"### Air Quality Index: {aqi}")
                                st.markdown(f"**{description}**")
                            
                            with col2:
                                # Display components
                                components_data = pollution_data.get('air_quality', {}).get('components', {})
                                
                                if components_data:
                                    st.markdown("**Components:**")
                                    st.markdown(f"PM2.5: {components_data.get('pm2_5', 0)} μg/m³")
                                    st.markdown(f"PM10: {components_data.get('pm10', 0)} μg/m³")
                                    st.markdown(f"NO₂: {components_data.get('no2', 0)} μg/m³")
                                    st.markdown(f"O₃: {components_data.get('o3', 0)} μg/m³")
                        else:
                            st.error(f"Error: {air_quality.get('error', 'Unknown error')}")

# News tab
elif st.session_state.current_tab == "news":
    st.header("📰 News")
    
    news_tabs = st.tabs(["Top Headlines", "Search News"])
    
    # Top Headlines tab
    with news_tabs[0]:
        st.subheader("Top Headlines")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            country = st.selectbox("Country:", [
                ("us", "United States"), 
                ("gb", "United Kingdom"), 
                ("ca", "Canada"), 
                ("au", "Australia"),
                ("de", "Germany"),
                ("fr", "France"),
                ("jp", "Japan"),
                ("in", "India")
            ], format_func=lambda x: x[1])
            
            category = st.selectbox("Category:", [
                ("", "All Categories"),
                ("business", "Business"),
                ("entertainment", "Entertainment"),
                ("general", "General"),
                ("health", "Health"),
                ("science", "Science"),
                ("sports", "Sports"),
                ("technology", "Technology")
            ], format_func=lambda x: x[1])
        
        with col2:
            page_size = st.slider("Number of articles:", min_value=5, max_value=20, value=10)
        
        if st.button("Get Headlines"):
            with st.spinner("Fetching headlines..."):
                news_api = components["news_api"]
                headlines = news_api.get_top_headlines(
                    country=country[0],
                    category=category[0] if category[0] else None,
                    page_size=page_size
                )
                
                st.session_state.news_data = headlines
        
        if st.session_state.news_data:
            if st.session_state.news_data.get('success', False):
                articles = st.session_state.news_data.get('headlines', [])
                
                if articles:
                    for article in articles:
                        st.markdown(f"### {article.get('title', '')}")
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**Source:** {article.get('source', {}).get('name', '')}")
                            
                            if article.get('description'):
                                st.markdown(article.get('description', ''))
                            
                            st.markdown(f"[Read more]({article.get('url', '')})")
                        
                        with col2:
                            if article.get('image_url'):
                                st.image(article.get('image_url', ''), use_column_width=True)
                        
                        st.markdown("---")
                else:
                    st.warning("No headlines found.")
            else:
                st.error(f"Error: {st.session_state.news_data.get('error', 'Unknown error')}")
    
    # Search News tab
    with news_tabs[1]:
        st.subheader("Search News")
        
        query = st.text_input("Search for news about:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            days = st.slider("Days to look back:", min_value=1, max_value=30, value=7)
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            to_date = datetime.now().strftime("%Y-%m-%d")
        
        with col2:
            language = st.selectbox("Language:", [
                ("en", "English"),
                ("es", "Spanish"),
                ("fr", "French"),
                ("de", "German"),
                ("it", "Italian"),
                ("ru", "Russian"),
                ("zh", "Chinese")
            ], format_func=lambda x: x[1])
            
            sort_by = st.selectbox("Sort by:", [
                ("publishedAt", "Published Date"),
                ("relevancy", "Relevance"),
                ("popularity", "Popularity")
            ], format_func=lambda x: x[1])
        
        if st.button("Search"):
            if query:
                with st.spinner("Searching news..."):
                    news_api = components["news_api"]
                    search_results = news_api.search_news(
                        query=query,
                        from_date=from_date,
                        to_date=to_date,
                        language=language[0],
                        sort_by=sort_by[0],
                        page_size=10
                    )
                    
                    st.session_state.search_results = search_results
            else:
                st.warning("Please enter a search query.")
        
        if "search_results" in st.session_state:
            if st.session_state.search_results.get('success', False):
                articles = st.session_state.search_results.get('articles', [])
                
                if articles:
                    # Option to summarize
                    if st.button("Summarize Results"):
                        with st.spinner("Generating summary..."):
                            summary = components["news_api"].summarize_news(articles, components["ai_engine"])
                            
                            if summary.get('success', False):
                                st.markdown("### Summary")
                                st.markdown(summary.get('summary', ''))
                                st.markdown("---")
                    
                    for article in articles:
                        st.markdown(f"### {article.get('title', '')}")
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**Source:** {article.get('source', {}).get('name', '')}")
                            
                            if article.get('description'):
                                st.markdown(article.get('description', ''))
                            
                            st.markdown(f"[Read more]({article.get('url', '')})")
                        
                        with col2:
                            if article.get('image_url'):
                                st.image(article.get('image_url', ''), use_column_width=True)
                        
                        st.markdown("---")
                else:
                    st.warning("No articles found matching your search criteria.")
            else:
                st.error(f"Error: {st.session_state.search_results.get('error', 'Unknown error')}")

# Settings tab
elif st.session_state.current_tab == "settings":
    st.header("⚙️ Settings")
    
    # API Keys
    st.subheader("API Keys")
    
    with st.expander("OpenAI API"):
        openai_key = st.text_input("OpenAI API Key:", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        if st.button("Save OpenAI Key"):
            # In a real app, this would securely save the API key
            st.success("OpenAI API key saved!")
    
    with st.expander("Financial APIs"):
        alpha_vantage_key = st.text_input("Alpha Vantage API Key:", type="password", value=os.getenv("ALPHA_VANTAGE_API_KEY", ""))
        finnhub_key = st.text_input("Finnhub API Key:", type="password", value=os.getenv("FINNHUB_API_KEY", ""))
        if st.button("Save Financial API Keys"):
            st.success("Financial API keys saved!")
    
    with st.expander("Weather API"):
        openweather_key = st.text_input("OpenWeather API Key:", type="password", value=os.getenv("OPENWEATHER_API_KEY", ""))
        if st.button("Save Weather API Key"):
            st.success("Weather API key saved!")
    
    with st.expander("News API"):
        newsapi_key = st.text_input("News API Key:", type="password", value=os.getenv("NEWSAPI_KEY", ""))
        if st.button("Save News API Key"):
            st.success("News API key saved!")
    
    # User Preferences
    st.subheader("User Preferences")
    
    theme = st.selectbox("Theme:", ["Light", "Dark"])
    language = st.selectbox("Language:", ["English", "Spanish", "French", "German"])
    
    if st.button("Save Preferences"):
        st.success("Preferences saved!")
    
    # Clear Data
    st.subheader("Data Management")
    
    if st.button("Clear Conversation History"):
        st.session_state.conversation_history = []
        st.success("Conversation history cleared!")
    
    if st.button("Clear All User Data"):
        if components["memory_manager"].delete_memory(st.session_state.current_user):
            st.success("All user data cleared!")
        else:
            st.error("Error clearing user data.")

# Run the app
def main():
    # This function is called when the script is run directly
    pass

if __name__ == "__main__":
    main()
