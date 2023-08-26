# thtmexicnkid
# Streamlit: D&D Note Input
# Author: Joe M
# Last Updated: Aug 22nd, 2023
# 
# Creates GUI for note input for D&D via Elastic

import json
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

character_to_index = {"Bengamin Bolton":"dnd-notes-bengamin_bolton","Corver Flickerspring":"dnd-notes-corver_flickerspring","Mae Avraya":"dnd-notes-mae_avraya", "Nyx":"dnd-notes-nyx", "Tanja":"dnd-notes-tanja"}
elastic_url = "https://localhost:9200"
elastic_ca_certs = "PATH TO ELASTIC CA CERT"
elastic_api_key = ("API_KEY_ID","API_KEY_VALUE")
streamlit_path = "PATH TO STREAMLIT FILE"

def app_page1():
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        try:
            name,authentication_status,username = authenticator.login("Login","main")
            if authentication_status:
                st.session_state.runpage = "app_page2"
                st.experimental_rerun()
            elif authentication_status == False:
                st.error('Username/password is incorrect')
            elif authentication_status == None:
                st.warning('Please enter your username and password')
        except:
            pass
    with tab2:
        try:
            if authenticator.register_user('Register', preauthorization=True):
                success('User registered successfully')
                update_yml()
        except Exception as e:
            st.error(e)

def app_page2():
    tab1, tab2 = st.tabs(["Note Input", "WIP - Ask Virtual DM"])
    with tab1:
        st.session_state["note_type"] = st.selectbox("Audio or Text?", ["Audio","Text"])
        if st.session_state["note_type"] == "Audio":
            log_index = "dnd-notes-transcribed"
            log_type = "audio"
            with st.form("audio_form", clear_on_submit=True):
                log_session = st.number_input("Which session is this?", 0, 250)
                file = st.file_uploader("Choose audio file",type=["mp3"])
                submitted = st.form_submit_button("Upload file")
                if submitted and file is not None:
                    transcribed_text = transcribe_audio(file.name)
                    if transcribed_text is not None:
                        log_payload = json.dumps({"session":log_session,"type":log_type,"message":transcribed_text})
                        elastic_index_document(log_index,log_payload)
                    else:
                        st.error("Audio transcription failure")
                else:
                    st.warning('Please upload a file and submit')
        elif st.session_state["note_type"] == "Text":
            log_type = st.selectbox("What kind of note is this?", ["location","overview","person","quest"])
            if log_type == "quest":
                with st.form("text_form_w_quest", clear_on_submit=True):
                    log_session = st.number_input("Which session is this?", 0, 250)
                    note_taker = st.selectbox("Who are you?", ["Bengamin Bolton","Corver Flickerspring","Mae Avraya", "Nyx", "Tanja"])
                    log_index = character_to_index[note_taker]
                    #I want to change this to a dropdown box populated with a list of available quest names from Elastic, if possible
                    quest_name = st.text_input("What is the name of the quest?")
                    quest_finished = st.checkbox("Is the quest finished?")
                    log_message = st.text_input("Input note text:")
                    submitted = st.form_submit_button("Upload note")
                    if submitted is not None:
                        log_payload = json.dumps({"finished":quest_finished,"message":log_message,"name":quest_name,"session":log_session,"type":log_type})
                        elastic_index_document(log_index,log_payload)
            else:
                with st.form("text_form_wo_quest", clear_on_submit=True):
                    log_session = st.number_input("Which session is this?", 0, 250)
                    note_taker = st.selectbox("Who are you?", ["Bengamin Bolton","Corver Flickerspring","Mae Avraya", "Nyx", "Tanja"])
                    log_index = character_to_index[note_taker]
                    log_message = st.text_input("Input note text:")
                    submitted = st.form_submit_button("Upload Note")
                    if submitted is not None:
                        log_payload = json.dumps({"message":log_message,"session":log_session,"type":log_type})
                        elastic_index_document(log_index,log_payload)
    with tab2:
        #I want to run notes through AI to be able to ask questions from this tab and receive answers
        pass
    authenticator.logout('Logout', 'main')

def clear_session_state(variable_list):
    for variable in variable_list:
        del st.session_state[variable]

def elastic_index_document(index,document):
    from elasticsearch import Elasticsearch
    
    # Connect to Elasticsearch
    client = Elasticsearch(
        elastic_url,
        ca_certs=elastic_ca_certs,
        api_key=elastic_api_key
    )
    
    # Send document to index
    response = client.index(index=index,document=document)
    
    if response["result"] == "created":
        success("Note creation successful")
    else:
        st.error("Note creation failure")
    
    client.close()
    response = None

def initialize_session_state(variable_list):
    for variable in variable_list:
        if variable not in st.session_state:
            st.session_state[variable] = None

def load_yml():
    with open(streamlit_path + "auth_config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    
    return authenticator

def success(text):
    import time
    
    success = st.success(text)
    time.sleep(1)
    success.empty()

def transcribe_audio(file):
    import assemblyai
    
    assemblyai.settings.api_key = "0a9d5171bf6e4f139121dcad4f622680"
    transcriber = assemblyai.Transcriber()
    transcript = transcriber.transcribe(streamlit_path + file)
    
    return transcript.text

def update_yml():
    with open(streamlit_path + "auth_config.yaml", 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

### PROGRAM ###
initialize_session_state(["username"])
authenticator = load_yml()

st.title("Elastic D&D")
st.session_state
if not st.session_state.username:
    st.session_state.runpage = app_page1
    st.session_state.runpage()
else:
    st.session_state.runpage = app_page2
    st.session_state.runpage()
