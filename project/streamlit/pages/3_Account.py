# Elastic D&D
# Author: thtmexicnkid
# Last Updated: 12/22/2023
# 
# Streamlit - Account Page - Allows the user to change their password and log out.

import streamlit as st
from functions import *
from variables import *

# set streamlit app to use whole screen
st.set_page_config(layout="centered")

# initializes session state, loads login authentication configuration, and performs index/data view setup in Elastic
initialize_session_state(["username","authentication_status"])
config, authenticator = load_yml()

# makes user log on to view page
if st.session_state.authentication_status in (False,None):
    error_message("UNAUTHORIZED: Please login on the Home page.",False)
else:
    with st.sidebar:
        # adds elastic d&d logo to sidebar
        display_image(streamlit_data_path + "banner.png","auto")
        st.divider()
        # add character picture to sidebar, if available
        try:
            display_image(streamlit_data_path + st.session_state.username + ".png","auto")
        except:
            print("Picture unavailable for home page sidebar.")
    st.header('Account',divider=True)
    try:
        if authenticator.reset_password(st.session_state.username, 'Reset password'):
            success_message('Password modified successfully')
            update_yml(config)
    except Exception as e:
        error_message(e,2)
    authenticator.logout('Logout', 'main')
