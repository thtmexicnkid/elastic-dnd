import streamlit as st
import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher(["YOUR_PASSWORD"]).generate()
st.text(hashed_passwords)