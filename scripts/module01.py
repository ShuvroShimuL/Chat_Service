"""
This module basically interact with user and checks the authenticity and stores user data in database.
"""

# Importing nesssary Modules
import streamlit as st
import pyrebase
import subprocess
from datetime import datetime
import os

"""
# Configuration key of firebase 
firebase_config = {
  "apiKey": "AIzaSyD7T9XpwAsjsbwWkJZQgaGQLYDG5EdrCgA",
  "authDomain": "project327-aee83.firebaseapp.com",
  "projectId": "project327-aee83",
  "databaseURL": "https://project327-aee83-default-rtdb.asia-southeast1.firebasedatabase.app/",
  "storageBucket": "project327-aee83.firebasestorage.app",
  "messagingSenderId": "629868004363",
  "appId": "1:629868004363:web:23e7d7ca2caf8f83cff30e",
  "measurementId": "G-1MN7NH2PVW"
}
"""

"""
# Initialization of firebase
firebase = pyrebase.initialize_app(firebase_config)
# Create the anchor to access the firebase
auth = firebase.auth()
# Create the database in firebase
db = firebase.database()


# Command to run chatbot
cmd = "streamlit run chatbot.py"
"""

# Login function in the page
def login():
    """
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")

    # If button actives then, (using exception handling to confirm the action)
    if st.button("Login"):
        try:
            # Checks whether the email and pass is macthed with existing email
            user = auth.sign_in_with_email_and_password(email, password)
            st.success("Logged in successfully!")
            # If login process occurs successfully then run the chatbot
            p = subprocess.Popen(cmd, shell = True)
            # Stop the current process
            os._exit(0)
        except Exception as e:
            st.warning("Incorrect email or Incorrect password!")
    """
    pass

# Sign up function in the page
def sign_up():
    """
    email = st.text_input("Email Address")
    password = st.text_input("Password(min 6 characters)", type="password")

    handle = st.text_input("Enter Your User Name")
    # If button actives then, (using exception handling to confirm the action)
    if st.button("Create my account"):
        try:
            # Create new user with email and password
            user = auth.create_user_with_email_and_password(email, password)
            st.success("Your account is created suceesfully!")
            st.balloons()
            # Checks whether the email and pass is macthed with existing email
            user = auth.sign_in_with_email_and_password(email, password)
            # Creates database entries with user informations
            db.child(user['localId']).child("Handle").set(handle)
            db.child(user['localId']).child("Email").set(email)
            db.child(user['localId']).child("ID").set(user['localId'])
            st.info("Login via login drop down selection")
            
        except Exception as e:
            st.warning("Already account exists with this email!")
    """
    pass



def main():
    """
    # Title and description
    st.title("Welcome to the chatbot!")
    choice = st.selectbox("Login/Signup",["Login","Sign up"])
    # Chose between selection box
    if choice == "Login":
        login()
    else:
        sign_up()
    """
    pass