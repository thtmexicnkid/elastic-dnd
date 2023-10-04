# Elastic D&D
# Author: thtmexicnkid
# Last Updated: 10/04/2023
# 
# Streamlit - Main Page - Displays a welcome message and explains how to navigate and use the application.

import streamlit as st
from functions import *
from variables import *

# displays application title
display_image(streamlit_data_path + "banner.png")

# initializes session state, loads login authentication configuration, and performs index/data view setup in Elastic
initialize_session_state(["username"])
config, authenticator = load_yml()
elastic_kibana_setup(config)

# makes user log on to view page
if not st.session_state.username:
    # displays login and registration widgets
    tab1, tab2 = st.tabs(["Login", "Register"])
    # login tab
    with tab1:
        try:
            name,authentication_status,username = authenticator.login("Login","main")
            if authentication_status:
                st.rerun()
            elif authentication_status == False:
                error_message('Username/password is incorrect')
            elif authentication_status == None:
                st.warning('Please enter your username and password')
        except:
            pass
    # registration tab
    with tab2:
        try:
            if authenticator.register_user('Register', preauthorization=True):
                success('User registered successfully')
                update_yml()
        except Exception as e:
            error_message(e)
else:
    st.header('Welcome!',divider=True)
    welcome_message = '''
    ## Elastic D&D is an ongoing project to facilitate note-taking and other functions derived from elements of D&D (virtual DM, roll data, etc.)
    
    ### You can navigate between pages of the application with the sidebar on the left:
    ##### The Home page is where you can go to refresh your memory on how to use the Elastic D&D application.
    ##### The Note Input page is used for storing notes for viewing and use with Virtual DM functions. Currently, you can input notes via an audio file or text.
    ##### The Virtual DM page is a work-in-progress. You will be able to ask it questions and it *should* return useful answers. "AI" is unpredictable when you are learning.
    ##### The Account page is used for changing your password and logging off.
    
    ### Stay up-to-date with the progress of this project on the [Github](https://github.com/thtmexicnkid/elastic-dnd)
    
    ## **Thanks for using Elastic D&D!**
    '''
    st.markdown(welcome_message)
