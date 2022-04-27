import streamlit as st
import streamlit_authenticator as stauth
from .database_utils import add_data, init_connection

names = ['Катя Такташева', 'Катя Волошина']
usernames = ['tak_ty', 'vokat']
passwords = ['123', '456']
hashed_passwords = stauth.Hasher(passwords).generate()
authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    'some_cookie_name', 'some_signature_key', cookie_expiry_days=30)

def app():
    name, authentication_status, username = authenticator.login('Login', 'main')
    if authentication_status:
        st.write('Добро пожаловать, *%s*' % name)
        db = init_connection()
        col1, col2 = st.columns([1, 8])
        with col2:
            st.header('Редактор базы данных')
        with col1:
            st.markdown(
                "<h1 style='text-align: center; font-size: 300%'>💻</h1>",
                unsafe_allow_html=True)
        upload_file = st.file_uploader('Выберите файл')
        if (upload_file is not None) and upload_file.name.endswith(".csv"):
            add_data(db, upload_file)
        else:
            st.markdown('Ничего не загружено или загружен неправильный файл')
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')