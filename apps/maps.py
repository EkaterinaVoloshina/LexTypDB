import lingtypology
import streamlit as st
import streamlit.components.v1 as components
from .database_utils import get_db

def app():
    db = get_db()
    languages = db.languages.find().distinct('lang')
    m = lingtypology.LingMap(languages)
    m.save('map.html')
    components.html(open('map.html', 'r', encoding='utf-8').read(), height=1500, width=1500)
