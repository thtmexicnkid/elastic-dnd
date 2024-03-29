# Elastic D&D
# Author: thtmexicnkid
# Last Updated: 01/12/2023
# 
# Streamlit - Home - Displays a dashboard of relevant information to the player
# WORK IN PROGRESS

import streamlit as st
from functions import *
from variables import *

# set streamlit app to use whole screen
st.set_page_config(layout="wide")

# initializes session state, loads login authentication configuration, and performs index/data view setup in Elastic
initialize_session_state(["username","authentication_status"])
config, authenticator = load_yml()
elastic_kibana_setup(config)

if st.session_state.authentication_status in (False,None):
    # displays elastic d&d logo as title image
    display_image(streamlit_data_path + "banner.png","auto")
    # displays login and registration widgets
    tab1, tab2 = st.tabs(["Login", "Register"])
    # login tab
    with tab1:
        try:
            name,authentication_status,username = authenticator.login("Login","main")
            if st.session_state.authentication_status:
                st.rerun()
            elif st.session_state.authentication_status == False:
                error_message('Username/password is incorrect')
            elif st.session_state.authentication_status == None:
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
    st.session_state["log_index"] = "dnd-notes-" + st.session_state.username
    # displays player welcome message
    st.markdown("<h1 style='text-align: center; color: white;'>Hello " + config["credentials"]["usernames"][st.session_state.username]["name"] + "!</h1>", unsafe_allow_html=True)
    st.session_state["last_session"], st.session_state["current_session"] = elastic_get_session_numbers(st.session_state.log_index)
    st.markdown("<h3 style='text-align: center; color: white;'>Prepare for session " + str(st.session_state.current_session) + "!</h3>", unsafe_allow_html=True)
    st.header("",divider="grey")
    # displays summary and active quest widgets
    column1, column2 = st.columns(2)
    with column1:
        st.header("Last Session:")
        st.markdown(elastic_get_previous_session_summary(st.session_state.log_index,st.session_state.last_session))
    with column2:
        st.header("Unfinished Quests:")
        quests = elastic_get_quests(st.session_state.log_index)
        for quest in quests:
            st.markdown("- " + quest)
    with st.sidebar:
        # adds elastic d&d logo to sidebar
        display_image(streamlit_data_path + "banner.png","auto")
        st.divider()
        # adds character picture to sidebar, if available
        try:
            display_image(streamlit_data_path + st.session_state.username + ".png","auto")
        except:
            print("Picture unavailable for home page sidebar.")
        st.divider()
        st.text("Current session: " + str(st.session_state.current_session))
