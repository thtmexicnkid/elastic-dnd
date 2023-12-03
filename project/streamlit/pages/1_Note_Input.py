# Elastic D&D
# Author: thtmexicnkid
# Last Updated: 11/03/2023
# 
# Streamlit - Note Input Page - Allows the user to store audio or text notes in Elasticsearch.

import streamlit as st
from functions import *
from variables import *

st.session_state

# displays application title and sets page accordingly
display_image(streamlit_data_path + "banner.png")

# initializes session state, loads login authentication configuration, and performs index/data view setup in Elastic
initialize_session_state(["username"])
config, authenticator = load_yml()

# makes user log on to view page
if not st.session_state.username:
    error_message("UNAUTHORIZED: Please login on the Home page.",False)
else:
    st.header('Note Input',divider=True)
    st.session_state["log_index"] = "dnd-notes-" + st.session_state.username
    st.session_state["note_type"] = st.selectbox("Audio or Text?", ["Audio","Text"], index=0)
    # runs app_page2_* functions depending on what is selected in selectbox
    if st.session_state.note_type == "Audio":
        #list of variables to clear from session state once finished
        audio_form_variable_list = ["log_type","log_session","file","submitted","transcribed_text","log_payload","log_id","content","content_vector"]
        
        if assemblyai_api_key:
            # displays note form widgets, creates note payload, sends payload to an Elastic index, and handles error / success / warning messages
            with st.form("audio_form", clear_on_submit=True):
                st.session_state["log_type"] = "audio"
                st.session_state["log_session"] = st.slider("Which session is this?", 0, 250)
                st.session_state["file"] = st.file_uploader("Choose audio file",type=[".3ga",".8svx",".aac",".ac3",".aif",".aiff",".alac",".amr",".ape",".au",".dss",".flac",".flv",".m2ts",".m4a",".m4b",".m4p",".m4p",".m4r",".m4v",".mogg",".mov",".mp2",".mp3",".mp4",".mpga",".mts",".mxf",".oga",".ogg",".opus",".qcp",".ts",".tta",".voc",".wav",".webm",".wma",".wv"])
                st.session_state["submitted"] = st.form_submit_button("Upload file")
                if st.session_state.submitted and st.session_state.file is not None:
                    # removes forward slash that will break the API call for AI functionality
                    st.session_state["transcribed_text"] = text_cleanup(transcribe_audio_paid(st.session_state.file))
                    if st.session_state.transcribed_text not in (None,""):
                        st.session_state["log_id"] = "session" + str(st.session_state.log_session) + "-" + generate_unique_id()
                        ### FOR LATER - check if log_id exists in elastic, re-generate_unique_id if it does ###
                        log_message_array = split_text_with_overlap(st.session_state.transcribed_text)
                        for log_message in log_message_array:
                            st.session_state["content"] = "This note took place in session " + str(st.session_state.log_session) + ". " + log_message
                            # gets vector object for use with AI functionality
                            st.session_state["content_vector"] = api_get_vector_object(st.session_state.content)
                            if st.session_state.content_vector == None:
                                error_message("AI API vectorization failure",2)
                            else:
                                st.session_state["log_payload"] = json.dumps({"session":st.session_state.log_session,"type":st.session_state.log_type,"message":st.session_state.transcribed_text,"message_vector":st.session_state.message_vector,"id":st.session_state.log_id,"content":st.session_state.content,"content_vector":st.session_state.content_vector})
                                elastic_index_document("dnd-notes-transcribed",st.session_state.log_payload,True)
                    else:
                        error_message("Audio transcription failure",2)
                else:
                    st.warning('Please upload a file and submit')
        else:
            # displays note form widgets, creates note payload, sends payload to an Elastic index, and handles error / success / warning messages
            with st.form("audio_form", clear_on_submit=True):
                st.session_state["log_type"] = "audio"
                st.session_state["log_session"] = st.slider("Which session is this?", 0, 250)
                st.session_state["file"] = st.file_uploader("Choose audio file",type=[".wav"])
                st.session_state["submitted"] = st.form_submit_button("Upload file")
                if st.session_state.submitted and st.session_state.file is not None:
                    # removes forward slash that will break the API call for AI functionality
                    st.session_state["transcribed_text"] = text_cleanup(transcribe_audio_free(st.session_state.file))
                    if st.session_state.transcribed_text not in (None,""):
                        st.session_state["log_id"] = "session" + str(st.session_state.log_session) + "-" + generate_unique_id()
                        ### FOR LATER - check if log_id exists in elastic, re-generate_unique_id if it does ###
                        log_message_array = split_text_with_overlap(st.session_state.transcribed_text)
                        for log_message in log_message_array:
                            st.session_state["content"] = "This note took place in session " + str(st.session_state.log_session) + ". " + log_message
                            # gets vector object for use with AI functionality
                            st.session_state["content_vector"] = api_get_vector_object(st.session_state.content)
                            if st.session_state.content_vector == None:
                                error_message("AI API vectorization failure",2)
                            else:
                                st.session_state["log_payload"] = json.dumps({"session":st.session_state.log_session,"type":st.session_state.log_type,"message":st.session_state.transcribed_text,"message_vector":st.session_state.message_vector,"id":st.session_state.log_id,"content":st.session_state.content,"content_vector":st.session_state.content_vector})
                                elastic_index_document("dnd-notes-transcribed",st.session_state.log_payload,True)
                    else:
                        error_message("Audio transcription failure",2)
                else:
                    st.warning('Please upload a file and submit')

        # clears session state
        clear_session_state(audio_form_variable_list)
    elif st.session_state.note_type == "Text":
        #list of variables to clear from session state once finished
        text_form_variable_list = ["log_type","log_session","note_taker","log_index","quest_type","quest_name","quest_finished","log_message","submitted","log_payload","log_id","content","content_vector"]

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
                    st.session_state["log_message"] = text_cleanup(st.text_area("Input note text:"))
                    st.session_state["submitted"] = st.form_submit_button("Upload note")
                    if st.session_state.submitted == True and st.session_state.log_message is not None:
                        st.session_state["log_id"] = "session" + str(st.session_state.log_session) + "-" + generate_unique_id()
                        ### FOR LATER - check if log_id exists in elastic, re-generate_unique_id if it does ###
                        log_message_array = split_text_with_overlap(st.session_state)
                        for log_message in log_message_array:
                            st.session_state["content"] = "This note took place in session " + str(st.session_state.log_session) + ". " + "The quest name is " + st.session_state.quest_name + ". " +  log_message
                            # gets vector object for use with AI functionality
                            st.session_state["content_vector"] = api_get_vector_object(st.session_state.content)
                            if st.session_state.content_vector == None:
                                error_message("AI API vectorization failure",2)
                            else:
                                st.session_state["log_payload"] = json.dumps({"finished":st.session_state.quest_finished,"id":st.session_state.log_id,"message":st.session_state.log_message,"session":st.session_state.log_session,"type":st.session_state.log_type,"content":st.session_state.content,"content_vector":st.session_state.content_vector,"name":st.session_state.quest_name})
                                elastic_index_document(st.session_state.log_index,st.session_state.log_payload,True)
                        st.rerun()
                    else:
                        st.warning('Please input note text and submit')
            else:
                quest_names = elastic_get_quests()
                with st.form("text_form_existing_quest", clear_on_submit=True):
                    st.session_state["log_session"] = st.slider("Which session is this?", 0, 250)
                    st.session_state["quest_name"] = st.selectbox("Which quest are you updating?", quest_names)
                    st.session_state["quest_finished"] = st.checkbox("Did you finish the quest?")
                    st.session_state["log_message"] = text_cleanup(st.text_area("Input note text:"))
                    st.session_state["submitted"] = st.form_submit_button("Upload note")
                    if st.session_state.submitted == True and st.session_state.log_message is not None:
                        # updates previous quest records to finished: true
                        if st.session_state.quest_finished == True:
                            elastic_update_quest_status(st.session_state.quest_name)
                        else:
                            pass
                        st.session_state["log_id"] = "session" + str(st.session_state.log_session) + "-" + generate_unique_id()
                        ### FOR LATER - check if log_id exists in elastic, re-generate_unique_id if it does ###
                        log_message_array = split_text_with_overlap(st.session_state)
                        for log_message in log_message_array:
                            st.session_state["content"] = "This note took place in session " + str(st.session_state.log_session) + ". " + "The quest name is " + st.session_state.quest_name + ". " + log_message
                            # gets vector object for use with AI functionality
                            st.session_state["content_vector"] = api_get_vector_object(st.session_state.content)
                            if st.session_state.content_vector == None:
                                error_message("AI API vectorization failure",2)
                            else:
                                st.session_state["log_payload"] = json.dumps({"finished":st.session_state.quest_finished,"id":st.session_state.log_id,"message":st.session_state.log_message,"session":st.session_state.log_session,"type":st.session_state.log_type,"content":st.session_state.content,"content_vector":st.session_state.content_vector,"name":st.session_state.quest_name})
                                elastic_index_document(st.session_state.log_index,st.session_state.log_payload,True)
                        st.rerun()
                    else:
                        st.warning('Please input note text and submit')
        # displays note form for all other log types
        else:
            with st.form("text_form_wo_quest", clear_on_submit=True):
                st.session_state["log_session"] = st.number_input("Which session is this?", 0, 250)
                st.session_state["log_message"] = text_cleanup(st.text_area("Input note text:"))
                st.session_state["submitted"] = st.form_submit_button("Upload Note")
                if st.session_state.submitted == True and st.session_state.log_message is not None:
                    st.session_state["log_id"] = "session" + str(st.session_state.log_session) + "-" + generate_unique_id()
                    ### FOR LATER - check if log_id exists in elastic, re-generate_unique_id if it does ###
                    log_message_array = split_text_with_overlap(st.session_state.log_message)
                    for log_message in log_message_array:
                        st.session_state["content"] = "This note took place in session " + str(st.session_state.log_session) + ". " + log_message
                        # gets vector object for use with AI functionality
                        st.session_state["content_vector"] = api_get_vector_object(st.session_state.content)
                        if st.session_state.content_vector == None:
                            error_message("AI API vectorization failure",2)
                        else:
                            st.session_state["log_payload"] = json.dumps({"id":st.session_state.log_id,"message":st.session_state.log_message,"session":st.session_state.log_session,"type":st.session_state.log_type,"content":st.session_state.content,"content_vector":st.session_state.content_vector})
                            elastic_index_document(st.session_state.log_index,st.session_state.log_payload,True)
                    st.rerun()
                else:
                    st.warning('Please input note text and submit')
        
        # clears session state
        clear_session_state(text_form_variable_list)
    else:
        pass
