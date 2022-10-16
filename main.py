import streamlit as st

from utils import load_data, view_products, recommend, view

st.title('Realtime recommendations based on Redis Vector Similarity Search and DocArray')

with st.spinner(text='Loading and indexing data...'):
    redis_da, colors, categories, countries, max_width, max_height = load_data()


with st.sidebar:
    color = st.selectbox(
        "Product color",
        colors
    )

    category = st.selectbox(
        "Product category",
        categories
    )

    country = st.selectbox(
        "Product country",
        countries
    )

    min_width, max_width = st.slider("Product width", min_value=0, max_value=max_width, value=(0, max_width))
    min_height, max_height = st.slider("Product height", min_value=0, max_value=max_height, value=(0, max_height))

products = recommend(st.session_state.get('view_history', []), redis_da, color=color, category=category,
                        country=country, min_width=min_width, max_width=max_width, min_height=min_height,
                        max_height=max_height)

if st.session_state.get('product'):
    view(st.session_state.get('product'), redis_da)
view_products(products)
