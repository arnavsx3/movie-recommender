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

with st.sidebar:
    st.header("Account")

    if st.session_state.token:
        st.success(f"Logged in as **{st.session_state.username}**")
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.username = None
            st.rerun()

    else:
        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

        with tab_login:
            login_email = st.text_input("Email", key="login_email")
            login_pass = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                r = api_post(
                    "/auth/login", {"email": login_email, "password": login_pass}
                )
                if r.status_code == 200:
                    data = r.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.username = data.get("username", login_email)
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Login failed"))

        with tab_signup:
            signup_username = st.text_input("Username", key="signup_username")
            signup_email = st.text_input("Email", key="signup_email")
            signup_pass = st.text_input("Password", type="password", key="signup_pass")
            if st.button("Sign Up"):
                r = api_post(
                    "/auth/signup",
                    {
                        "username": signup_username,
                        "email": signup_email,
                        "password": signup_pass,
                    },
                )
                if r.status_code == 201:
                    st.success("Account created! Please log in.")
                else:
                    st.error(r.json().get("detail", "Signup failed"))
