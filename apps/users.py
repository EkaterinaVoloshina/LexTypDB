import streamlit as st
from .database_utils import add_data, init_connection


def app():
    login = st.text_input("Login:")
    access_token = st.text_input("Password:", type="password")
    if login and access_token != st.secrets["users"][login]:
        st.write("Sorry, your token is invalid. Please try again or contact the administrator.")
    else:
        col1, col2 = st.columns([1, 8])
        with col2:
                st.header('Редактор базы данных')
        with col1:
                st.markdown(
                    "<h1 style='text-align: center; font-size: 300%'>💻</h1>",
                    unsafe_allow_html=True)
        upload_file = st.file_uploader('Выберите файл')
        if (upload_file is not None) and upload_file.name.endswith(".csv"):
            db = init_connection()
            add_data(db, upload_file)
        else:
            st.markdown('Ничего не загружено или загружен неправильный файл')
