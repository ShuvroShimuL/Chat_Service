# Project_CSE327

Use **Python 3.12.6** & `virtualenv` to avoid any unwanted dependency conflict behaviors.

## Welcome to the Chat_Service wiki!
### Steps to create `virtualenv`:
1. Download the directory.
2. open `cmd` in your preferred directory.
3. Install virtualenv using `pip install virtualenv`.
4. Open `cmd` in the directory and type `python -m venv myenv` to create virtualenv.
5. Now, if you are in the same directory in `cmd`, then type `myenv\Scripts\activate` to activate the environment.
### Steps to run the Chatbot:
1. If you are in the same directory in `cmd`, then type `pip install -r requirements.txt` to install the necessary dependencies.
2. Set your credentials in the same terminal:

   ```cmd
   set FIREBASE_API_KEY=your-firebase-api-key
   set GROQ_API_KEY=your-groq-api-key
   ```

   In PowerShell, use `$env:FIREBASE_API_KEY="your-firebase-api-key"` and `$env:GROQ_API_KEY="your-groq-api-key"` instead.
3. Then, type `python exe.py` to run the application and log in. Login, chat, and logout use one Streamlit server; authentication and chat history belong to each browser session.
4. Type a question and press **Send** (or Enter), or use the microphone button. **Exit** logs out and clears your chat history.

The default Groq model is `openai/gpt-oss-120b`, listed in [Groq's supported models](https://console.groq.com/docs/models). To select another model available to your account, set `GROQ_MODEL` before starting the application.

Firebase Realtime Database rules should require authenticated writes and restrict each user's profile to their own UID. Signup passes the new user's ID token when saving their profile.

Run the regression tests with `python -m unittest discover -v`. The tests mock Firebase, Groq, and microphone access and do not require credentials or network access.

