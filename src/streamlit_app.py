import streamlit as st
import os
import sys
import openai
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

# Set page configuration
st.set_page_config(
    page_title="Open Manus AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for conversation history
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Function to get response from OpenAI API
def get_openai_response(prompt, conversation_history):
    try:
        messages = []
        # Add system message
        messages.append({"role": "system", "content": "You are Open Manus AI, a helpful assistant with advanced capabilities in conversation, task automation, coding support, and financial analysis."})
        
        # Add conversation history
        for message in conversation_history:
            messages.append({"role": message["role"], "content": message["content"]})
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling OpenAI API: {str(e)}")
        return f"I apologize, but I encountered an error: {str(e)}. Please try again later."

# Sidebar for navigation
st.sidebar.title("Open Manus AI")
st.sidebar.image("https://raw.githubusercontent.com/dantiezsaunderson/Open_Manus_AI/master/docs/logo.png", use_column_width=True)

# Navigation
page = st.sidebar.radio("Navigate", ["Conversation", "Task Automation", "Coding Support", "Financial Analysis"])

# Main content area
st.title(f"Open Manus AI - {page}")

if page == "Conversation":
    st.write("Chat with your AI assistant powered by GPT-4.")
    
    # Display conversation history
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**AI:** {message['content']}")
    
    # Input for new message
    user_input = st.text_input("Type your message:", key="user_input")
    
    if st.button("Send"):
        if user_input:
            # Add user message to history
            st.session_state.conversation_history.append({"role": "user", "content": user_input})
            
            # Get AI response from OpenAI
            ai_response = get_openai_response(user_input, st.session_state.conversation_history[:-1])
            
            # Add AI response to history
            st.session_state.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Clear input and rerun to show updated conversation
            st.rerun()

elif page == "Task Automation":
    st.write("Automate tasks with your AI assistant.")
    
    task_type = st.selectbox("Select task type:", ["Email Drafting", "Meeting Summary", "Research", "Data Analysis", "Custom Task"])
    
    if task_type == "Custom Task":
        task_description = st.text_area("Describe your task:")
    else:
        task_description = st.text_area("Provide details for your task:")
    
    if st.button("Execute Task"):
        if task_description:
            st.info("Task submitted for processing...")
            
            # Get AI response for task
            prompt = f"Task type: {task_type}\nTask description: {task_description}\nPlease complete this task."
            ai_response = get_openai_response(prompt, [])
            
            st.success("Task completed!")
            st.markdown(f"**Result:**\n{ai_response}")

elif page == "Coding Support":
    st.write("Get help with coding and development.")
    
    code_language = st.selectbox("Programming Language:", ["Python", "JavaScript", "Java", "C++", "Go", "Other"])
    
    code_question = st.text_area("Enter your code or describe your coding question:")
    
    if st.button("Get Code Help"):
        if code_question:
            # Get AI response for coding question
            prompt = f"I need help with {code_language} code. Here's my question or code:\n\n{code_question}"
            ai_response = get_openai_response(prompt, [])
            
            st.markdown("### Solution")
            st.markdown(ai_response)

elif page == "Financial Analysis":
    st.write("Analyze financial data and get insights.")
    
    analysis_type = st.selectbox("Analysis Type:", ["Stock Analysis", "Portfolio Optimization", "Market Trends", "Economic Indicators"])
    
    if analysis_type == "Stock Analysis":
        ticker = st.text_input("Enter stock ticker symbol (e.g., AAPL):")
        
        if st.button("Analyze"):
            if ticker:
                st.info(f"Analyzing {ticker}...")
                
                # Get AI response for stock analysis
                prompt = f"Perform a detailed analysis of {ticker} stock. Include current price, market cap, P/E ratio, recent performance, and future outlook."
                ai_response = get_openai_response(prompt, [])
                
                st.markdown("### Analysis Results")
                st.markdown(ai_response)
                
                # Create placeholder charts (in a real implementation, these would be actual stock data)
                st.subheader("Stock Price (Last 12 Months)")
                chart_data = {"Date": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                             "Price": [150, 155, 160, 158, 162, 165, 170, 175, 172, 178, 180, 185]}
                st.line_chart(chart_data, x="Date", y="Price")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Open Manus AI - Your Personal AI Assistant")
st.sidebar.markdown("Version 1.1.0")
