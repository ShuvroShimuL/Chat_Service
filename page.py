# Importing nesssary Modules
import streamlit as st
import pyrebase
import os
import re

from chatbot import main as chat_main
from session_auth import is_authenticated, start_session

# Configuration key of firebase
firebase_config = {
  "apiKey": os.environ.get("FIREBASE_API_KEY", "Your API Key"),
  "authDomain": "project327-aee83.firebaseapp.com",
  "projectId": "project327-aee83",
  "databaseURL": "https://project327-aee83-default-rtdb.asia-southeast1.firebasedatabase.app/",
  "storageBucket": "project327-aee83.firebasestorage.app",
  "messagingSenderId": "629868004363",
  "appId": "1:629868004363:web:23e7d7ca2caf8f83cff30e",
  "measurementId": "G-1MN7NH2PVW"
}


# Initialization of firebase
firebase = pyrebase.initialize_app(firebase_config)
# Create the anchor to access the firebase
auth = firebase.auth()
# Create the database in firebase
db = firebase.database()

# Login function in the page
def login():
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")

    # If button actives then, (using exception handling to confirm the action)
    if st.button("Login"):
        try:
            # Checks whether the email and pass is macthed with existing email
            user = auth.sign_in_with_email_and_password(email, password)
            start_session(user)
        except Exception:
            st.warning("Incorrect email or Incorrect password!")
            return

        st.success("Logged in successfully!")
        st.rerun()

# Sign up function in the page
def sign_up():
    email = st.text_input("Email Address")
    password = st.text_input("Password(min 6 characters)", type="password")

    handle = st.text_input("Enter Your User Name").strip()
    # If button actives then, (using exception handling to confirm the action)
    if st.button("Create my account"):
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            st.warning("Please enter a valid email address")
            return
        if len(password) < 6:
            st.warning("Password must be at least 6 characters long")
            return
        if len(handle) == 0:
            st.warning("Please enter a valid user name")
            return

        try:
            # Create new user with email and password
            user = auth.create_user_with_email_and_password(email, password)
        except Exception:
            st.warning(
                "Could not create your account. Check the email and password, "
                "or try logging in if you already have an account."
            )
            return

        try:
            # Creates database entries with user informations
            db.child(user['localId']).set({
                "Handle": handle,
                "Email": email,
                "ID": user['localId']
            }, user['idToken'])
        except Exception:
            st.warning(
                "Your account was created, but your profile could not be saved. "
                "You can still log in."
            )
            return

        st.success("Your account is created successfully!")
        st.balloons()
        st.info("Login via login drop down selection")


def main():
    if is_authenticated():
        chat_main()
        return

    # Title and description
    st.title("Welcome to the chatbot!")
    choice = st.selectbox("Login/Signup",["Login","Sign up"])
    # Chose between selection box
    if choice == "Login":
        login()
    else:
        sign_up()


if __name__ == "__main__":
    main()
