import streamlit as st
import pandas as pd
from .database_utils import *

def app():
    login = st.text_input("Login:")
    access_token = st.text_input("Password:", type="password")
    button = st.button("Log in")
    if button:
        if access_token == st.secrets["users"][login]:
            col1, col2 = st.columns([1, 8])
            with col2:
                    st.header('Редактор базы данных')
            with col1:
                    st.markdown(
                        "<h1 style='text-align: center; font-size: 300%'>💻</h1>",
                        unsafe_allow_html=True)
            with st.expander("Инструкция"):
                st.markdown("В таблице должны быть столбцы со следующими названиями:")
                st.markdown("**Language**: проверьте, что название вашего языка записано **по-английски** так же, как в WALS и других базах.")
                st.markdown("**Field**: название поля (на русском), например, *менять*.")
                st.markdown("**Frame**: название фрейма (на русском).")
                st.markdown("**Context**: название микрофрейма (на русском).")
                st.markdown("**Verb**: глагол, использующийся в примере (на Вашем языке).")
                st.markdown("**Example**: пример на нужный микрофрейм.")
                st.markdown("**Translation**: перевод на русский.")
                st.markdown("**Speakers**: процентное число носителей, которые назвали этот глагол.")

            format = st.radio('How to upload?', ['Fill in a form', 'Upload a table'])
            if format == "Fill in a form":
                data = fill_in_form("my_form")
                df = pd.DataFrame(data)
                db = init_connection()
                add_data(db, df)
            else:
                upload_file = st.file_uploader('Выберите файл')
                columns = ["Language", "Field", "Frame", "Context",
                           "Verb", "Example", "Translation"]
                if (upload_file is not None) and upload_file.name.endswith(".csv"):
                    if set(upload_file.columns) == set(columns):
                        db = init_connection()
                        add_data(db, upload_file)
                    else:
                        missing_cols = set(columns).difference(set(upload_file.columns))
                        st.markdown(f"The columns {*missing_cols} are missing. Upload a new file.")
                else:
                    st.markdown('Ничего не загружено или загружен неправильный файл')
        else:
            st.write("Sorry, your token is invalid. Please try again or contact the administrator.")
