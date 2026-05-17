import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

# Load API key
load_dotenv(override=True)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Page title
st.title("🤖 Ketan's First AI Chatbot")
st.write("Powered by Groq AI - Free & Fast!")

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

    # Get Groq response
    try:
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.messages
            )
            ai_response = response.choices[0].message.content

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