import streamlit as st
from .utils import *
import pymongo

def app():
    mongo = "mongodb+srv://dep:utJyKHbMFwNACwwl@cluster0.e1rwx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
    client = pymongo.MongoClient(mongo)
    db = client.lextyp

    st.subheader('Поиск по примерам')
    text = st.text_input(
        label='',
        #placeholder='прятать язык',
        key='полнотекстовый поиск'
    )

    field = st.multiselect(
        label='Семантическое поле:',
        options=sorted(db.fields.find().distinct("field")),
        #               key=lambda x: x.split()[-1]),
    )


    col1, col2 = st.columns([5, 5])
    with col1:
        language = st.multiselect(
            label='Язык:',
            options=sorted(db.languages.find().distinct("lang")),
            #               key=lambda x: x.split()[-1]),
        )
    with col2:
        verb = st.multiselect(
            label='Глаголы:',
            options=sorted(db.verbs.find().distinct("verb")),
            #               key=lambda x: x.split()[-1]),
        )
    col1, col2 = st.columns([5, 5])
    with col1:
        frames = st.multiselect(
            label='Фреймы:',
            options=sorted(db.fields.find().distinct("fields.frame")),
        )
    with col2:
        context = st.multiselect(
            label='Контексты:',
            options=sorted(db.contexts.find().distinct("context")),
        )
    button = st.button("Search")
    if button:
        res = list(fulltext_search(db, text, verb, language, field, frames, context))
        st.code(verb, language)
        if len(res) == 0:
            st.markdown("Нет результатов")
        else:
            for result in res:
                st.markdown(f"`{result['frames']['field'].upper()}` — **{result['languages']['verb']}** ({result['languages']['language']})")
                st.markdown(f"{result['frames']['frame']}: {result['frames']['context']}")
                st.markdown("**ПРИМЕР**")
                st.markdown(result["examples"]["example"])
                st.markdown(result["examples"]["translation"])

