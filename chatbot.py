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

# Command to run chatbot
cmd = "streamlit run page.py"

# Set the memory length for the conversation
conversational_memory_length = 10
memory = ConversationBufferWindowMemory(k=conversational_memory_length)

# Collecting user question
def get_user_input():
    user_question = st.text_input("Ask a question:")
    if st.button("🎙️"):
        user_question = voice_interact()
    get_response(user_question)

# Voice interact
def voice_interact():
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

# Generate user response
def get_response(user_question):
    # Initialize session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "conversation" not in st.session_state:
        # Retrieve Groq API Key from environment
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            st.error("GROQ_API_KEY environment variable is not set. Please configure it to use the chatbot.")
            return

        # Initialize Groq Langchain chat object and conversation
        groq_chat = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama3-70b-8192"
        )
        # Built-in function in conversation langchain framework
        st.session_state.conversation = ConversationChain(
            llm=groq_chat,
            memory=memory
        )

    conversation = st.session_state.conversation

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

    except Exception:
            st.warning("Something Happened!")

    st.text(" ")
    st.text(" ")

    if st.button("Exit"):
        exit_from_chatbot()

# Exit from current page
def exit_from_chatbot():
    p = subprocess.Popen(cmd, shell = True)
    os._exit(0)



if __name__ == "__main__":
    # Title and description
    st.title("Chat with 🚀")
    st.write("Hello, I'm your friendly chatbot! You can ask me anything, feel free to ask...")

    get_user_input()
