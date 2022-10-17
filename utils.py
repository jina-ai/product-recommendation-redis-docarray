import functools
import os

import numpy as np
from docarray import DocumentArray, Document
import streamlit as st


@st.cache(persist=True)
def load_data():
    da = DocumentArray.pull(os.getenv('DATASET_NAME', 'amazon-berkeley-objects-dataset-encoded'), show_progress=True)
    colors = [None] + list({doc.tags['color'] for doc in da})
    categories = [None] + list({doc.tags['product_type'] for doc in da})
    countries = [None] + list({doc.tags['country'] for doc in da})
    max_width = max({int(doc.tags['width']) for doc in da})
    max_height = max({int(doc.tags['height']) for doc in da})
    redis_da = DocumentArray(storage='redis', config={
        # uncomment if you're using Redis cloud
        # 'host': 'host',
        # 'port': 'port',
        # 'redis_config': {
        #     'password': 'password'
        # },
        'n_dim': 768,
        'columns': {
            'color': 'str',
            'country': 'str',
            'product_type': 'str',
            'width': 'int',
            'height': 'int',
            'brand': 'str',
        }, 'tag_indices': ['item_name']
    })
    redis_da.extend(da)
    return redis_da, colors, categories, countries, max_width, max_height


def recommend(view_history, da: DocumentArray, k: int = 10, color=None, category=None, country=None, min_width=None, max_width=None,
              min_height=None, max_height=None):
    user_filter = {}
    if color:
        user_filter['color'] = {'$eq': color}

    if country:
        user_filter['country'] = {'$eq': country}

    if category:
        user_filter['product_type'] = {'$eq': category}

    width_filter = {}
    if max_width:
        width_filter['$lte'] = max_width
    if min_width:
        width_filter['$gte'] = min_width

    if width_filter:
        user_filter['width'] = width_filter

    height_filter = {}
    if max_height:
        height_filter['$lte'] = max_height
    if min_height:
        height_filter['$gte'] = min_height

    if height_filter:
        user_filter['height'] = height_filter

    if view_history:
        embedding = np.average(
            [doc.embedding for doc in view_history],
            weights=range(len(view_history), 0, -1),
            axis=0
        )
        return da.find(embedding, filter=user_filter, limit=k)
    else:
        return da.find(filter=user_filter, limit=k)


def view(product_id: str, da: DocumentArray):
    image_column, info_column = st.columns(2)
    doc = da[product_id]
    image_column.image(doc.uri)
    info_column.write(f'Name: {doc.tags["item_name"]}')
    info_column.write(f'Category: {doc.tags["product_type"]}')
    info_column.write(f'Brand: {doc.tags["brand"]}')
    info_column.write(f'Width: {doc.tags["width"]}')
    info_column.write(f'Height: {doc.tags["height"]}')

    del st.session_state['product']



def set_viewed_product(product: Document, k: int = 10):
    st.session_state['product'] = product.id
    view_history = st.session_state.get('view_history', [])
    view_history.insert(0, product)
    view_history = view_history[:k]
    st.session_state['view_history'] = view_history


def view_products(docs, k: int = 10):
    columns = st.columns(k)
    for doc, column in zip(docs[:k], columns):
        container = column.container()
        container.button('view', on_click=functools.partial(set_viewed_product, product=doc, k=k), key=doc.id)
        container.image(doc.uri, use_column_width='always')

