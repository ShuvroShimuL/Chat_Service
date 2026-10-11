"""Authentication and chat state belonging to the current browser session."""

import streamlit as st


def _valid_user(user):
    return isinstance(user, dict) and all(
        isinstance(user.get(key), str) and bool(user[key])
        for key in ("localId", "idToken")
    )


def is_authenticated():
    return _valid_user(st.session_state.get("user"))


def clear_session():
    for key in ("user", "conversation", "chat_history"):
        st.session_state.pop(key, None)


def start_session(user):
    if not _valid_user(user):
        raise ValueError("Firebase did not return an authenticated user")
    clear_session()
    st.session_state["user"] = user
