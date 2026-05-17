import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Setup Gemini model
model = genai.GenerativeModel("gemini-2.5-flash-lite")

# Page title
st.title("🤖 Ketan's First AI Chatbot")
st.write("Powered by Google Gemini - Free!")

# Store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("Type your message here..."):

    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Build history for Gemini
    history = []
    for msg in st.session_state.messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append({
            "role": role,
            "parts": [msg["content"]]
        })

    # Start chat with history
    chat = model.start_chat(history=history)

   # Get Gemini response with timeout handling
import google.api_core.exceptions
try:
    chat = model.start_chat(history=history)
    response = chat.send_message(
        prompt,
        request_options={"timeout": 60}
    )
    ai_response = response.text
except google.api_core.exceptions.DeadlineExceeded:
    ai_response = "Request timed out. Please try again!"
except Exception as e:
    ai_response = f"Error: {str(e)}"

    # Show AI response
    with st.chat_message("assistant"):
        st.markdown(ai_response)

    # Save AI response
    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_response
    })