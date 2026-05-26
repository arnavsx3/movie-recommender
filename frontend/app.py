import streamlit as st
import requests

API_BASE = "http://localhost:8000"

if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
