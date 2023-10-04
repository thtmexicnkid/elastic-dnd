# Elastic D&D
# Author: thtmexicnkid
# Last Updated: 10/03/2023
# 
# Streamlit - Note Input Page - Allows the user to store audio or text notes in Elasticsearch.

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
    st.header('Note Input',divider=True)
    st.session_state["log_index"] = "dnd-notes-" + st.session_state.username
    st.session_state["note_type"] = st.selectbox("Audio or Text?", ["Audio","Text"], index=0)
    # runs app_page2_* functions depending on what is selected in selectbox
    if st.session_state.note_type == "Audio":
        #list of variables to clear from session state once finished
        audio_form_variable_list = ["log_type","log_session","file","submitted","transcribed_text","log_payload","message_vector"]
        
        # displays note form widgets, creates note payload, sends payload to an Elastic index, and handles error / success / warning messages
        with st.form("audio_form", clear_on_submit=True):
            st.session_state["log_type"] = "audio"
            st.session_state["log_session"] = st.slider("Which session is this?", 0, 250)
            st.session_state["file"] = st.file_uploader("Choose audio file",type=[".3ga",".8svx",".aac",".ac3",".aif",".aiff",".alac",".amr",".ape",".au",".dss",".flac",".flv",".m2ts",".m4a",".m4b",".m4p",".m4p",".m4r",".m4v",".mogg",".mov",".mp2",".mp3",".mp4",".mpga",".mts",".mxf",".oga",".ogg",".opus",".qcp",".ts",".tta",".voc",".wav",".webm",".wma",".wv"])
            st.session_state["submitted"] = st.form_submit_button("Upload file")
            if st.session_state.submitted and st.session_state.file is not None:
                # removes forward slash that will break the API call for AI functionality
                st.session_state["transcribed_text"] = (transcribe_audio(st.session_state.file)).replace("/", " or ")
                if st.session_state.transcribed_text is not None:
                    # gets vector object for use with AI functionality
                    st.session_state["message_vector"] = api_get_vector_object(st.session_state.transcribed_text)
                    if st.session_state.message_vector == None:
                        error_message("AI API vectorization failure",2)
                    else:
                        st.session_state["log_payload"] = json.dumps({"session":st.session_state.log_session,"type":st.session_state.log_type,"message":st.session_state.transcribed_text,"message_vector":st.session_state.message_vector})
                        elastic_index_document("dnd-notes-transcribed",st.session_state.log_payload)
                else:
                    error_message("Audio transcription failure",2)
            else:
                st.warning('Please upload a file and submit')
        
        # clears session state
        clear_session_state(audio_form_variable_list)
    elif st.session_state.note_type == "Text":
        #list of variables to clear from session state once finished
        text_form_variable_list = ["log_type","log_session","note_taker","log_index","quest_type","quest_name","quest_finished","log_message","submitted","log_payload","message_vector"]

        # displays note form widgets, creates note payload, sends payload to an Elastic index, and handles error / success / warning messages
        st.session_state["log_type"] = st.selectbox("What kind of note is this?", ["location","miscellaneous","overview","person","quest"])
        # displays note form for quest log type
        if st.session_state.log_type == "quest":
            st.session_state["quest_type"] = st.selectbox("Is this a new or existing quest?", ["New","Existing"])
            if st.session_state.quest_type == "New":
                with st.form("text_form_new_quest", clear_on_submit=True):
                    st.session_state["log_session"] = st.slider("Which session is this?", 0, 250)
                    st.session_state["quest_name"] = st.text_input("What is the name of the quest?")
                    st.session_state["quest_finished"] = st.checkbox("Did you finish the quest?")
                    # removes forward slash that will break the API call for AI functionality
                    st.session_state["log_message"] = (st.text_area("Input note text:")).replace("/", " or ")
                    st.session_state["submitted"] = st.form_submit_button("Upload note")
                    if st.session_state.submitted == True and st.session_state.log_message is not None:
                        # gets vector object for use with AI functionality
                        st.session_state["message_vector"] = api_get_vector_object(st.session_state.log_message)
                        if st.session_state.message_vector == None:
                            error_message("AI API vectorization failure",2)
                        else:
                            st.session_state["log_payload"] = json.dumps({"finished":st.session_state.quest_finished,"message":st.session_state.log_message,"name":st.session_state.quest_name,"session":st.session_state.log_session,"type":st.session_state.log_type,"message_vector":st.session_state.message_vector})
                            elastic_index_document(st.session_state.log_index,st.session_state.log_payload)
                            st.rerun()
                    else:
                        st.warning('Please input note text and submit')
            else:
                quest_names = elastic_get_quests()
                with st.form("text_form_existing_quest", clear_on_submit=True):
                    st.session_state["log_session"] = st.slider("Which session is this?", 0, 250)
                    st.session_state["quest_name"] = st.selectbox("Which quest are you updating?", quest_names)
                    st.session_state["quest_finished"] = st.checkbox("Did you finish the quest?")
                    st.session_state["log_message"] = (st.text_area("Input note text:")).replace("/", " or ")
                    st.session_state["submitted"] = st.form_submit_button("Upload note")
                    if st.session_state.submitted == True and st.session_state.log_message is not None:
                        # updates previous quest records to finished: true
                        if st.session_state.quest_finished == True:
                            elastic_update_quest_status(st.session_state.quest_name)
                        else:
                            pass
                        # gets vector object for use with AI functionality
                        st.session_state["message_vector"] = api_get_vector_object(st.session_state.log_message)
                        if st.session_state.message_vector == None:
                            error_message("AI API vectorization failure",2)
                        else:
                            st.session_state["log_payload"] = json.dumps({"finished":st.session_state.quest_finished,"message":st.session_state.log_message,"name":st.session_state.quest_name,"session":st.session_state.log_session,"type":st.session_state.log_type,"message_vector":st.session_state.message_vector})
                            elastic_index_document(st.session_state.log_index,st.session_state.log_payload)
                            st.rerun()
                    else:
                        st.warning('Please input note text and submit')
        # displays note form for all other log types
        else:
            with st.form("text_form_wo_quest", clear_on_submit=True):
                st.session_state["log_session"] = st.number_input("Which session is this?", 0, 250)
                st.session_state["log_message"] = (st.text_area("Input note text:")).replace("/", " or ")
                st.session_state["submitted"] = st.form_submit_button("Upload Note")
                if st.session_state.submitted == True and st.session_state.log_message is not None:
                    # gets vector object for use with AI functionality
                    st.session_state["message_vector"] = api_get_vector_object(st.session_state.log_message)
                    if st.session_state.message_vector == None:
                        error_message("AI API vectorization failure",2)
                    else:
                        st.session_state["log_payload"] = json.dumps({"message":st.session_state.log_message,"session":st.session_state.log_session,"type":st.session_state.log_type,"message_vector":st.session_state.message_vector})
                        elastic_index_document(st.session_state.log_index,st.session_state.log_payload)
                        st.rerun()
                else:
                    st.warning('Please input note text and submit')
        
        # clears session state
        clear_session_state(text_form_variable_list)
    else:
        pass
