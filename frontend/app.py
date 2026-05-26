import streamlit as st
import requests

API_BASE = "http://localhost:8000"

if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None

def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def api_post(endpoint: str, payload: dict, auth: bool = False):
    headers = auth_headers() if auth else {}
    r = requests.post(f"{API_BASE}{endpoint}", json=payload, headers=headers)
    return r


def api_get(endpoint: str, params: dict = {}, auth: bool = False):
    headers = auth_headers() if auth else {}
    r = requests.get(f"{API_BASE}{endpoint}", params=params, headers=headers)
    return r