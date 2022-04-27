import lingtypology
import streamlit as st
import streamlit.components.v1 as components
from .database_utils import init_connection, find_languages

def app():
    db = init_connection()
    languages = db.languages.find().distinct('lang')
    name = st.multiselect(
        label='Язык:',
        options=languages,
        )
    st.text(name)
    button = st.button("Search")
    if button:
        if name:
            results = find_languages(db, name)
            languages = [result['lang'] for result in results]
            st.code(languages)
        m = lingtypology.LingMap(languages)
        m.save('map.html')
        components.html(open('map.html', 'r', encoding='utf-8').read(), height=1500, width=1500)
