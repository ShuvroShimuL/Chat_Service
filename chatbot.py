"""Chat UI served inside the authenticated Streamlit application."""

import os

import speech_recognition as sr
import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from session_auth import clear_session, is_authenticated


DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
LOGIN_REQUIRED = "Please log in through the login page to use the chatbot."
conversational_memory_length = 10


def get_user_input():
    if not is_authenticated():
        st.warning(LOGIN_REQUIRED)
        return

    # Handle logout before any submission or model request.
    if st.button("Exit"):
        exit_from_chatbot()
        return

    for message in st.session_state.get("chat_history", []):
        st.write("You: " + message["human"])
        st.write("Chatbot 🤖: " + message["AI"])

    with st.form("chat_question", clear_on_submit=True):
        user_question = st.text_input("Ask a question:")
        submitted = st.form_submit_button("Send")

    if st.button("🎙️"):
        user_question = voice_interact()
        submitted = True

    if submitted:
        if user_question and user_question.strip():
            get_response(user_question.strip())
        elif user_question is not None:
            st.warning("Please enter a question.")


def voice_interact():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            audio = recognizer.listen(source, timeout=20)
            user_question = recognizer.recognize_google(audio)
            st.text("🗣 : " + user_question)
            return user_question
    except Exception:
        st.warning("Failed to understand!")


def get_response(user_question):
    if not is_authenticated():
        st.warning(LOGIN_REQUIRED)
        return
    if not user_question or not user_question.strip():
        return

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    try:
        if "conversation" not in st.session_state:
            groq_api_key = os.environ.get("GROQ_API_KEY")
            if not groq_api_key:
                st.error(
                    "GROQ_API_KEY environment variable is not set. "
                    "Please configure it to use the chatbot."
                )
                return

            groq_chat = ChatGroq(
                groq_api_key=groq_api_key,
                model_name=os.environ.get("GROQ_MODEL") or DEFAULT_GROQ_MODEL,
            )
            st.session_state["conversation"] = ConversationChain(
                llm=groq_chat,
                memory=ConversationBufferWindowMemory(k=conversational_memory_length),
            )

        response = st.session_state["conversation"].predict(input=user_question)
        st.session_state["chat_history"].append(
            {"human": user_question, "AI": response}
        )
        st.write("Chatbot 🤖: " + response)
        st.success("Response generated successfully!")
    except Exception:
        st.warning("Could not generate a response. Please try again.")


def exit_from_chatbot():
    clear_session()
    st.rerun()


def main():
    if not is_authenticated():
        st.warning(LOGIN_REQUIRED)
        return

    st.title("Chat with 🚀")
    st.write(
        "Hello, I'm your friendly chatbot! You can ask me anything, feel free to ask..."
    )
    get_user_input()


if __name__ == "__main__":
    main()
