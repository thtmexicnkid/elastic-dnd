# Elastic D&D
# Author: thtmexicnkid
# Last Updated: 01/12/2023
# 
# Streamlit - Note Input Page - Allows the user to store audio or text notes in Elasticsearch.

import streamlit as st
from functions import *
from variables import *

# set streamlit app to use centered format
st.set_page_config(layout="wide")

# initializes session state, loads login authentication configuration
initialize_session_state(["username","authentication_status"])
config, authenticator = load_yml()

# makes user log on to view page
if st.session_state.authentication_status in (False,None):
    error_message("UNAUTHORIZED: Please login on the Home page.",False)
else:
    st.header("Note Input",divider="grey")
    # gather information for log_payload in form
    form_variable_list = ["log_id","log_type","log_session","log_index","file","location_name","location_description","overview_summary","person_name","person_description","quest_name","quest_description","quest_finished","submitted","transcribed_text","content","content_vector"]
    st.session_state["log_type"] = st.selectbox("What kind of note is this?", ["audio","location","miscellaneous","overview","person","quest"])
    if st.session_state.log_type == "quest":
        st.session_state["quest_type"] = st.selectbox("Is this quest new or existing?", ["New","Existing"])
    with st.form(st.session_state.log_type, clear_on_submit=True):
        st.session_state["log_session"] = st.slider("Which session is this?", 0, 250)
        st.session_state["log_id"] = "session" + str(st.session_state.log_session) + "-" + generate_unique_id()
        ###CHECK IF LOG_ID EXISTS, RE-GENERATE IF IT DOES###
        if st.session_state.log_type == "audio":
            st.session_state["log_index"] = "dnd-notes-transcribed"
            if assemblyai_api_key:
                st.session_state["file"] = st.file_uploader("Choose audio file",type=[".3ga",".8svx",".aac",".ac3",".aif",".aiff",".alac",".amr",".ape",".au",".dss",".flac",".flv",".m2ts",".m4a",".m4b",".m4p",".m4p",".m4r",".m4v",".mogg",".mov",".mp2",".mp3",".mp4",".mpga",".mts",".mxf",".oga",".ogg",".opus",".qcp",".ts",".tta",".voc",".wav",".webm",".wma",".wv"])
            else:
                st.session_state["file"] = st.file_uploader("Choose audio file",type=[".wav"])
            if st.session_state.file is not None:
                st.session_state["ready_for_submission"] = True
            else:
                st.warning('Please upload a file and submit')
        else:
            st.session_state["log_index"] = "dnd-notes-" + st.session_state.username
            if st.session_state.log_type == "location":
                st.session_state["location_name"] = text_cleanup(st.text_input("Input location name:"))
                st.session_state["location_description"] = text_cleanup(st.text_area("Input location description:"))
                if st.session_state.location_name is not None and st.session_state.location_description is not None:
                    st.session_state["ready_for_submission"] = True
                else:
                    st.warning('Please enter the location name, description, and submit')
            elif st.session_state.log_type == "miscellaneous":
                st.session_state["miscellaneous_note"] = text_cleanup(st.text_area("Input miscellaneous note:"))
                if st.session_state.miscellaneous_note is not None:
                    st.session_state["ready_for_submission"] = True
                else:
                    st.warning('Please enter miscellaneous note and submit')
            elif st.session_state.log_type == "overview":
                st.session_state["overview_summary"] = text_cleanup(st.text_area("Input session summary:"))
                if st.session_state.overview_summary is not None:
                    st.session_state["ready_for_submission"] = True
                else:
                    st.warning('Please enter the session overview/summary and submit')
            elif st.session_state.log_type == "person":
                st.session_state["person_name"] = text_cleanup(st.text_input("Input person name:"))
                st.session_state["person_description"] = text_cleanup(st.text_area("Input person description:"))
                if st.session_state.person_name is not None and st.session_state.person_description is not None:
                    st.session_state["ready_for_submission"] = True
                else:
                    st.warning('Please enter the person name, description, and submit')
            elif st.session_state.log_type == "quest":
                if st.session_state.quest_type == "Existing":
                    st.session_state["quest_name"] = st.selectbox("Select quest to update", elastic_get_quests(st.session_state.log_index))
                else:
                    st.session_state["quest_name"] = st.text_input("Input quest name:")
                st.session_state["quest_description"] = text_cleanup(st.text_area("Input quest description / update:"))
                st.session_state["quest_finished"] = st.checkbox("Is the quest finished?")
                if st.session_state.quest_name is not None and st.session_state.quest_description is not None:
                    st.session_state["ready_for_submission"] = True
                else:
                    st.warning('Please enter the quest name, description, mark the status, and submit')
        # submit form, process data, and index log_payload
        st.session_state["submitted"] = st.form_submit_button("Submit")
        if st.session_state.submitted == True and st.session_state.ready_for_submission == True:
            # audio to text transcription
            if st.session_state.log_type == "audio":
                if assemblyai_api_key:
                    st.session_state["transcribed_text"] = text_cleanup(transcribe_audio_paid(st.session_state.file))
                else:
                    st.session_state["transcribed_text"] = text_cleanup(transcribe_audio_free(st.session_state.file))
                if st.session_state.transcribed_text not in (None,""):
                    chunk_array = split_text_with_overlap(st.session_state.transcribed_text)
                    for chunk in chunk_array:
                        st.session_state["content"] = "This note is from session " + str(st.session_state.log_session) + ". " + chunk
                        st.session_state["content_vector"] = api_get_vector_object(st.session_state.content)
                        if st.session_state.content_vector == None:
                            error_message("AI API vectorization failure",2)
                        else:
                            st.session_state["log_payload"] = json.dumps({"id":st.session_state.log_id,"type":st.session_state.log_type,"session":st.session_state.log_session,"message":st.session_state.transcribed_text,"content":st.session_state.content,"content_vector":st.session_state.content_vector})
                            elastic_index_document(st.session_state.log_index,st.session_state.log_payload,True)
            # location logs
            elif st.session_state.log_type == "location":
                chunk_array = split_text_with_overlap(st.session_state.location_description)
                for chunk in chunk_array:
                    st.session_state["content"] = "This note is from session " + str(st.session_state.log_session) + ". The location is " + st.session_state.location_name + ". " + chunk
                    st.session_state["content_vector"] = api_get_vector_object(st.session_state.content)
                    if st.session_state.content_vector == None:
                        error_message("AI API vectorization failure",2)
                    else:
                        st.session_state["log_payload"] = json.dumps({"id":st.session_state.log_id,"type":st.session_state.log_type,"session":st.session_state.log_session,"message":st.session_state.location_name + ". " + st.session_state.location_description,"content":st.session_state.content,"content_vector":st.session_state.content_vector,"location":{"name":st.session_state.location_name,"description":st.session_state.location_description}})
                        elastic_index_document(st.session_state.log_index,st.session_state.log_payload,True)
            # miscellaneous logs
            elif st.session_state.log_type == "miscellaneous":
                chunk_array = split_text_with_overlap(st.session_state.miscellaneous_note)
                for chunk in chunk_array:
                    st.session_state["content"] = "This note is from session " + str(st.session_state.log_session) + ". " + chunk
                    st.session_state["content_vector"] = api_get_vector_object(st.session_state.content)
                    if st.session_state.content_vector == None:
                        error_message("AI API vectorization failure",2)
                    else:
                        st.session_state["log_payload"] = json.dumps({"id":st.session_state.log_id,"type":st.session_state.log_type,"session":st.session_state.log_session,"message":st.session_state.miscellaneous_note,"content":st.session_state.content,"content_vector":st.session_state.content_vector})
                        elastic_index_document(st.session_state.log_index,st.session_state.log_payload,True)
            # overview logs
            elif st.session_state.log_type == "overview":
                chunk_array = split_text_with_overlap(st.session_state.overview_summary)
                for chunk in chunk_array:
                    st.session_state["content"] = "This note is from session " + str(st.session_state.log_session) + ". " + chunk
                    st.session_state["content_vector"] = api_get_vector_object(st.session_state.content)
                    if st.session_state.content_vector == None:
                        error_message("AI API vectorization failure",2)
                    else:
                        st.session_state["log_payload"] = json.dumps({"id":st.session_state.log_id,"type":st.session_state.log_type,"session":st.session_state.log_session,"message":st.session_state.overview_summary,"content":st.session_state.content,"content_vector":st.session_state.content_vector})
                        elastic_index_document(st.session_state.log_index,st.session_state.log_payload,True)
            # person logs
            elif st.session_state.log_type == "person":
                chunk_array = split_text_with_overlap(st.session_state.person_description)
                for chunk in chunk_array:
                    st.session_state["content"] = "This note is from session " + str(st.session_state.log_session) + ". The person's name is " + st.session_state.person_name + ". " + chunk
                    st.session_state["content_vector"] = api_get_vector_object(st.session_state.content)
                    if st.session_state.content_vector == None:
                        error_message("AI API vectorization failure",2)
                    else:
                        st.session_state["log_payload"] = json.dumps({"id":st.session_state.log_id,"type":st.session_state.log_type,"session":st.session_state.log_session,"message":st.session_state.person_name + ". " + st.session_state.person_description,"content":st.session_state.content,"content_vector":st.session_state.content_vector,"person":{"name":st.session_state.person_name,"description":st.session_state.person_description}})
                        elastic_index_document(st.session_state.log_index,st.session_state.log_payload,True)
            # quest logs
            elif st.session_state.log_type == "quest":
                if st.session_state.quest_finished == True:
                    elastic_update_quest_status(st.session_state.quest_name)
                    status = "The quest has been completed."
                else:
                    status = "The quest has not been completed yet."
                chunk_array = split_text_with_overlap(st.session_state.quest_description)
                for chunk in chunk_array:
                    st.session_state["content"] = "This note is from session " + str(st.session_state.log_session) + ". The quest is " + st.session_state.quest_name + ". " + status + " " + chunk
                    st.session_state["content_vector"] = api_get_vector_object(st.session_state.content)
                    if st.session_state.content_vector == None:
                        error_message("AI API vectorization failure",2)
                    else:
                        st.session_state["log_payload"] = json.dumps({"id":st.session_state.log_id,"type":st.session_state.log_type,"session":st.session_state.log_session,"message":st.session_state.quest_name + ". " + st.session_state.quest_description + status,"content":st.session_state.content,"content_vector":st.session_state.content_vector,"quest":{"name":st.session_state.quest_name,"description":st.session_state.quest_description,"finished":st.session_state.quest_finished}})
                        elastic_index_document(st.session_state.log_index,st.session_state.log_payload,True)
    with st.sidebar:
        # adds elastic d&d logo to sidebar
        display_image(streamlit_data_path + "banner.png","auto")
        st.divider()
        # add character picture to sidebar, if available
        try:
            display_image(streamlit_data_path + st.session_state.username + ".png","auto")
        except:
            print("Picture unavailable for home page sidebar.")
        st.divider()
        st.text("Current session: " + str(st.session_state.current_session))
        
    clear_session_state(form_variable_list)
