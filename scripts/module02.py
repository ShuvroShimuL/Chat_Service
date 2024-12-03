"""
This module collects user queries and generate response using langchain. It also holds history of the conversation to main the contextual conversation. 
"""

# Importing nesssary Modules
import streamlit as st 
from langchain_core.messages import SystemMessage
from groq import Groq
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
import subprocess
import speech_recognition as sr
import os
"""
# Command to run chatbot
cmd = "streamlit run page.py"

# Set the memory length for the conversation
conversational_memory_length = 10
memory = ConversationBufferWindowMemory(k=conversational_memory_length)
"""

# Collecting user question
def get_user_input():
    """
    user_question = st.text_input("Ask a question:")
    if st.button("🎙️"):
        user_question = voice_interact()
    get_response(user_question)
    """
    pass

# Voice interact
def voice_interact():
    """
    # Obtain audio from the microphone
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            audio = r.listen(source, timeout=20)
            user_question = r.recognize_google(audio)
            st.text("🗣 : " + user_question)
            return user_question
    except Exception as e:
        st.warning("Failed to understand!")
    """
    pass

# Generate user response
def get_response(user_question):
    """
    # Initialize session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    else:
        # Restore chat history in memory
        for message in st.session_state.chat_history:
            memory.save_context(
                {"input": message["human"]},  
                {"output": message["AI"]}    
            )

    # Initialize Groq Langchain chat object and conversation
    groq_chat = ChatGroq(
        groq_api_key="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", 
        model_name="llama3-70b-8192"
    )
    # Built-in function in conversation langchain framework
    conversation = ConversationChain(
        llm=groq_chat,
        memory=memory
    )

    try:
        # Get the response using the correct key
        response = conversation.predict(input=user_question)  # Fixed key
        # Save the interaction in session state
        message = {"human": user_question, "AI": response}
        st.session_state.chat_history.append(message)
        
        # Display the chatbot's response
        st.write("Chatbot 🤖: " + response)
        if message:
            st.success("Response genereated successfully!")
                
    except Exception as e:
            st.warning("Something Happened!")
    
    st.text(" ")
    st.text(" ")
    
    if st.button("Exit"):
        exit_from_chatbot()
    """
    pass

# Exit from the current page 
def exit_from_chatbot():
    """
    p = subprocess.Popen(cmd, shell = True)
    os._exit(0)
    """
    pass
    
 
def main():
    """
    # Title and description
    st.title("Chat with 🚀")
    st.write("Hello, I'm your friendly chatbot! You can ask me anything, feel free to ask...")

    get_user_input()
    """
    pass