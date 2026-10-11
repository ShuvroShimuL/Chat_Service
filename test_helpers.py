"""Load application modules with isolated external-service mocks."""

import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


USER = {"localId": "user123", "idToken": "test-token"}


def load_app():
    dependencies = {
        name: MagicMock()
        for name in (
            "streamlit", "pyrebase", "speech_recognition", "langchain",
            "langchain.chains", "langchain.chains.conversation",
            "langchain.chains.conversation.memory", "langchain_groq",
        )
    }
    ui = dependencies["streamlit"]
    ui.session_state = {}
    ui.button.return_value = False
    ui.form_submit_button.return_value = False
    modules = {}
    with patch.dict(sys.modules, dependencies):
        for name in ("session_auth", "chatbot", "page"):
            path = Path(__file__).parent / (name + ".py")
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            modules[name] = module
    return SimpleNamespace(st=ui, dependencies=dependencies, **modules)
