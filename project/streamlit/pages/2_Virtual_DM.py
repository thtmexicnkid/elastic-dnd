# Elastic D&D
# Author: thtmexicnkid
# Last Updated: 10/03/2023
# 
# Streamlit - Virtual DM Page - Allows the user to ask questions and receive answers automatically.

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
    st.header('Virtual DM',divider=True)
