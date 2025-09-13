# application.py
import os
import pickle
import requests
import streamlit as st

# Try Streamlit secrets first (works on Streamlit Cloud), fallback to env var
TMDB_API_KEY = None
try:
    TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
except Exception:
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if not TMDB_API_KEY:
    st.warning("TMDB_API_KEY not found in st.secrets or environment variables. Poster images may fail.")

@st.cache_data(show_spinner=False)  # use st.cache if your Streamlit version is older
def fetch_poster(movie_id):
    if not TMDB_API_KEY:
        return None
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    resp = requests.get(url, timeout=5)
    if resp.status_code != 200:
        return None
    data = resp.json()
    poster_path = data.get("poster_path")
    if not poster_path:
        return None
    return f"https://image.tmdb.org/t/p/w500{poster_path}"

def recommend(movie, movies_df, similarity_matrix):
    idx = movies_df[movies_df['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity_matrix[idx])), reverse=True, key=lambda x: x[1])
    names, posters = [], []
    for i in distances[1:6]:
        movie_id = movies_df.iloc[i[0]].movie_id
        names.append(movies_df.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))
    return names, posters

st.header("Movie Recommender System")

# load pickles (ensure model/ exists and contains the pickles)
movies = pickle.load(open('model/movie_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

if st.button("Show Recommendation"):
    recommended_names, recommended_posters = recommend(selected_movie, movies, similarity)
    cols = st.columns(5)
    for col, name, poster in zip(cols, recommended_names, recommended_posters):
        with col:
            st.write(name)
            if poster:
                st.image(poster, use_container_width=True)
            else:
                st.write("Poster not found")





