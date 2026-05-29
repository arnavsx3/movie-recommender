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

st.title("🎬 Movie Recommender")

tab_recommend, tab_search, tab_rate = st.tabs(["Recommend", "Search", "My Ratings"])

with tab_recommend:
    st.subheader("Get recommendations by title")
    movie = st.text_input("Movie title", key="rec_title")
    alpha = st.slider(
        "Personalization blend",
        0.0,
        1.0,
        0.5,
        0.1,
        help="1.0 = content only, 0.0 = collaborative only",
    )
    n = st.slider("Number of results", 5, 50, 10, key="rec_n")

    if st.button("Recommend"):
        if not movie:
            st.warning("Enter a movie title.")
        else:
            params = {"title": movie, "n": n, "alpha": alpha}
            r = api_get(
                "/movies/recommend", params=params, auth=bool(st.session_state.token)
            )
            if r.status_code == 200:
                data = r.json()
                st.markdown(f"**Recommendations for:** {data['title']}")
                for i, rec in enumerate(data["recommendations"], 1):
                    source_badge = "🔀" if rec.get("source") == "hybrid" else "📄"
                    st.write(
                        f"{i}. {source_badge} **{rec['title']}** — score: `{rec['score']}`"
                    )
            else:
                st.error(r.json().get("detail", "Something went wrong"))
