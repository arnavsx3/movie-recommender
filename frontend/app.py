import streamlit as st

st.title("Movie Recommender")
st.write("Enter a movie to get recommendations!")

movie = st.text_input("Movie title")

if st.button("Recommend"):
    st.write(f"Recommendations for **{movie}** coming soon...")
