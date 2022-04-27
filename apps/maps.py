import lingtypology
import streamlit as st
import streamlit.components.v1 as components
from .database_utils import init_connection, find_languages

def app():
    db = init_connection()
    languages = list(db.languages.find().distinct('lang'))
    options = languages.append("all")
    name = st.selectbox(
        label='Язык:',
        options=options
    )
    button = st.button("Search")
    if button:
        if name != 'all':
            results = find_languages(db, name)
            languages = [result['lang'] for result in results]
        m = lingtypology.LingMap(languages)
        m.save('map.html')
        components.html(open('map.html', 'r', encoding='utf-8').read(), height=1500, width=1500)
