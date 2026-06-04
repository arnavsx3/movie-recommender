import streamlit as st
import requests
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE = "http://localhost:8000"
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w300"
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"

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

def get_poster_url(title: str) -> str | None:
    try:
        r = requests.get(
            TMDB_SEARCH_URL,
            params={"api_key": TMDB_API_KEY, "query": title},
            timeout=5,
        )
        data = r.json()
        results = data.get("results", [])
        if results and results[0].get("poster_path"):
            return TMDB_IMAGE_BASE + results[0]["poster_path"]
    except Exception:
        pass
    return None

def render_movie_card(rank: int, title: str, score: float, source: str):
    source_badge = "🔀 Hybrid" if source == "hybrid" else "📄 Content"
    poster_url = get_poster_url(title)

    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            if poster_url:
                st.image(poster_url, width=100)
            else:
                st.markdown("🎬")
        with col2:
            st.markdown(f"**{rank}. {title}**")
            st.caption(f"Score: `{score}` · {source_badge}")
        st.divider()


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


with tab_search:
    st.subheader("Search movies by description")
    query = st.text_input("Describe what you want to watch", key="search_query")
    n2 = st.slider("Number of results", 5, 50, 10, key="search_n")

    if st.button("Search"):
        if not query:
            st.warning("Enter a search query.")
        else:
            params = {"q": query, "n": n2}
            r = api_get(
                "/movies/search", params=params, auth=bool(st.session_state.token)
            )
            if r.status_code == 200:
                data = r.json()
                st.markdown(f"**Results for:** {data['query']}")
                for i, rec in enumerate(data["results"], 1):
                    source_badge = "🔀" if rec.get("source") == "hybrid" else "📄"
                    st.write(
                        f"{i}. {source_badge} **{rec['title']}** — score: `{rec['score']}`"
                    )
            else:
                st.error(r.json().get("detail", "Something went wrong"))


with tab_rate:
    st.subheader("Rate a movie")

    if not st.session_state.token:
        st.info("Log in to rate movies and get personalized recommendations.")
    else:
        # Submit a rating
        with st.form("rate_form"):
            movie_id = st.text_input("Movie ID (UUID)")
            rating_val = st.slider("Rating", 0.5, 5.0, 3.0, 0.5)
            submitted = st.form_submit_button("Submit Rating")

            if submitted:
                if not movie_id:
                    st.warning("Enter a movie ID.")
                else:
                    r = api_post(
                        "/ratings/",
                        {"movie_id": movie_id, "rating": rating_val},
                        auth=True,
                    )
                    if r.status_code == 200:
                        st.success("Rating submitted!")
                    else:
                        st.error(r.json().get("detail", "Failed to submit rating"))

        # View my ratings
        st.divider()
        st.subheader("My Ratings")
        if st.button("Load my ratings"):
            import jwt

            try:
                payload = jwt.decode(
                    st.session_state.token,
                    algorithms=["HS256"],
                    options={"verify_signature": False},
                )

                user_id = payload.get("sub")
                r = api_get(f"/ratings/{user_id}", auth=True)
                if r.status_code == 200:
                    ratings = r.json()
                    if not ratings:
                        st.info("No ratings yet.")
                    else:
                        for rating in ratings:
                            st.write(f"🎬 `{rating['movie_id']}` —  {rating['rating']}")
                else:
                    st.error(r.json().get("detail", "Failed to load ratings"))
            except Exception as e:
                st.error(f"Could not decode token: {e}")
