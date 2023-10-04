# Elastic D&D
# Author: thtmexicnkid
# Last Updated: 10/03/2023
# 
# Streamlit - Account Page - Allows the user to change their password and log out.

import streamlit as st
from functions import *
from variables import *

# displays application title and sets page accordingly
display_image(streamlit_data_path + "banner.png")

# initializes session state, loads login authentication configuration, and performs index/data view setup in Elastic
initialize_session_state(["username"])
config, authenticator = load_yml()

# makes user log on to view page
if not st.session_state.username:
    error_message("UNAUTHORIZED: Please login on the Home page.",10)
else:
    st.header('Account',divider=True)
    try:
        if authenticator.reset_password(st.session_state.username, 'Reset password'):
            success_message('Password modified successfully')
            update_yml()
    except Exception as e:
        error_message(e,2)
    authenticator.logout('Logout', 'main')
