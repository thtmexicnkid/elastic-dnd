# Elastic D&D
# Author: thtmexicnkid
# Last Updated: 08/28/2023
# 
# Streamlit app that allows for D&D note-taking into Elastic by text or audio.

import streamlit as st
import streamlit_authenticator as stauth

### STATIC VARIABLES ###
# *** change this to fit your environment ***
character_to_index = {"Bengamin Bolton":"dnd-notes-bengamin_bolton","Corver Flickerspring":"dnd-notes-corver_flickerspring","Mae Avraya":"dnd-notes-mae_avraya", "Nyx":"dnd-notes-nyx", "Tanja":"dnd-notes-tanja"}
elastic_url = "ELASTIC_URL"
elastic_ca_certs = "PATH_TO_ELASTIC_CA.crt"
elastic_api_key = ("API_KEY_ID","API_KEY")
streamlit_path = "PATH_TO_STREAMLIT_SCRIPT"

### FUNCTIONS ###
def app_page1():
    # displays login and registration widgets
    tab1, tab2 = st.tabs(["Login", "Register"])
    # login tab
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
    # registration tab
    with tab2:
        try:
            if authenticator.register_user('Register', preauthorization=True):
                success('User registered successfully')
                update_yml()
        except Exception as e:
            st.error(e)

def app_page2():
    # displays note input and virtual DM widgets
    tab1, tab2 = st.tabs(["Note Input", "WIP - Ask Virtual DM"])
    # note input tab
    with tab1:
        st.session_state["note_type"] = st.selectbox("Audio or Text?", ["Audio","Text"], index=0)
        # runs app_page2_* functions depending on what is selected in selectbox
        if st.session_state.note_type == "Audio":
            st.session_state.runpage = app_page2_audio
            st.session_state.runpage()
            # if session state is empty, re-run the page
            if st.session_state == {}:
                st.session_state.runpage = app_page2_audio
                st.experimental_rerun()
        elif st.session_state.note_type == "Text":
            st.session_state.runpage = app_page2_text
            st.session_state.runpage()
            # if session state is empty, re-run the page
            if st.session_state == {}:
                st.session_state.runpage = app_page2_text
                st.experimental_rerun()
        else:
            pass
    # virtual DM tab
    with tab2:
        #I want to run notes through AI to be able to ask questions from this tab and receive answers
        pass
    
    # logout button
    authenticator.logout('Logout', 'main')
    
def app_page2_audio():
    # displays audio note form and widgets
    import json
    
    #list of variables to clear from session state once finished
    audio_form_variable_list = ["log_index","log_type","log_session","file","submitted","transcribed_text","log_payload"]
    
    # displays note form widgets, creates note payload, sends payload to an Elastic index, and handles error / success / warning messages
    with st.form("audio_form", clear_on_submit=True):
        st.session_state["log_index"] = "dnd-notes-transcribed"
        st.session_state["log_type"] = "audio"
        st.session_state["log_session"] = st.slider("Which session is this?", 0, 250)
        st.session_state["file"] = st.file_uploader("Choose audio file",type=["mp3"])
        st.session_state["submitted"] = st.form_submit_button("Upload file")

        if st.session_state.submitted and st.session_state.file is not None:
            st.session_state["transcribed_text"] = transcribe_audio(st.session_state.file.name)
            if st.session_state.transcribed_text is not None:
                st.session_state["log_payload"] = json.dumps({"session":st.session_state.log_session,"type":st.session_state.log_type,"message":st.session_state.transcribed_text})
                elastic_index_document(st.session_state.log_index,st.session_state.log_payload)
            else:
                error_message("Audio transcription failure")
        else:
            st.warning('Please upload a file and submit')
    
    # clears session state
    clear_session_state(audio_form_variable_list)
    
def app_page2_text():
    # displays text note form and widgets
    import json
    
    #list of variables to clear from session state once finished
    text_form_variable_list = ["log_type","log_session","note_taker","log_index","quest_name","quest_finished","log_message","submitted","log_payload"]

    # displays note form widgets, creates note payload, sends payload to an Elastic index, and handles error / success / warning messages
    st.session_state["log_type"] = st.selectbox("What kind of note is this?", ["location","overview","person","quest"])
    # displays note form for quest log type
    if st.session_state.log_type == "quest":
        with st.form("text_form_w_quest", clear_on_submit=True):
            st.session_state["log_session"] = st.slider("Which session is this?", 0, 250)
            st.session_state["note_taker"] = st.selectbox("Who are you?", ["Bengamin Bolton","Corver Flickerspring","Mae Avraya", "Nyx", "Tanja"])
            st.session_state["log_index"] = character_to_index[st.session_state.note_taker]
            #I want to change this to a dropdown box populated with a list of available quest names from Elastic, if possible
            st.session_state["quest_name"] = st.text_input("What is the name of the quest?")
            st.session_state["quest_finished"] = st.checkbox("Is the quest finished?")
            st.session_state["log_message"] = st.text_input("Input note text:")
            st.session_state["submitted"] = st.form_submit_button("Upload note")
            if st.session_state.submitted == True and st.session_state.log_message is not None:
                st.session_state["log_payload"] = json.dumps({"finished":st.session_state.quest_finished,"message":st.session_state.log_message,"name":st.session_state.quest_name,"session":st.session_state.log_session,"type":st.session_state.log_type})
                elastic_index_document(st.session_state.log_index,st.session_state.log_payload)
                st.experimental_rerun()
            else:
                st.warning('Please input note text and submit')
    # displays note form for all other log types
    else:
        with st.form("text_form_wo_quest", clear_on_submit=True):
            st.session_state["log_session"] = st.number_input("Which session is this?", 0, 250)
            st.session_state["note_taker"] = st.selectbox("Who are you?", ["Bengamin Bolton","Corver Flickerspring","Mae Avraya", "Nyx", "Tanja"])
            st.session_state["log_index"] = character_to_index[st.session_state.note_taker]
            st.session_state["log_message"] = st.text_input("Input note text:")
            st.session_state["submitted"] = st.form_submit_button("Upload Note")
            if st.session_state.submitted == True and st.session_state.log_message is not None:
                st.session_state["log_payload"] = json.dumps({"message":st.session_state.log_message,"session":st.session_state.log_session,"type":st.session_state.log_type})
                elastic_index_document(st.session_state.log_index,st.session_state.log_payload)
                st.experimental_rerun()
            else:
                st.warning('Please input note text and submit')
    
    # clears session state
    clear_session_state(text_form_variable_list)

def clear_session_state(variable_list):
    # deletes variables from streamlit session state
    for variable in variable_list:
        try:
            del st.session_state[variable]
        except:
            pass

def display_image(image_path):
    # displays an image via path relative to streamlit app script
    from PIL import Image

    image = Image.open(image_path)
    st.image(image)

def elastic_index_document(index,document):
    # sends a document to an Elastic index
    from elasticsearch import Elasticsearch
    
    # creates Elastic connection
    client = Elasticsearch(
        elastic_url,
        ca_certs=elastic_ca_certs,
        api_key=elastic_api_key
    )
    
    # sends document to index with success or failure message
    response = client.index(index=index,document=document)
    
    if response["result"] == "created":
        success_message("Note creation successful")
    else:
        error_message("Note creation failure")
    
    # close Elastic connection
    client.close()

def error_message(text):
    # displays error message
    import time
    
    error = st.error(text)
    time.sleep(1)
    error.empty()

def initialize_session_state(variable_list):
    # creates empty variables in streamlit session state
    for variable in variable_list:
        if variable not in st.session_state:
            st.session_state[variable] = None

def load_yml():
    # loads login authentication configuration
    import yaml
    from yaml.loader import SafeLoader
    
    with open(streamlit_path + "streamlit-auth.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    
    return authenticator

def success_message(text):
    # displays success message
    import time
    
    success = st.success(text)
    time.sleep(1)
    success.empty()

def transcribe_audio(file):
    # transcribes an audio file to text
    import assemblyai
    
    # *** AssemblyAI API KEY, you need to set this ***
    assemblyai.settings.api_key = "API_KEY"
    transcriber = assemblyai.Transcriber()
    transcript = transcriber.transcribe(streamlit_path + file)
    
    return transcript.text

def update_yml():
    # updates login authentication configuration file
    import yaml
    
    with open(streamlit_path + "streamlit-auth.yaml", 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

### PROGRAM ###

# initializes session state and loads login authentication configuration
initialize_session_state(["username"])
authenticator = load_yml()

# displays application title and sets page accordingly
display_image("banner.png")
if not st.session_state.username:
    st.session_state.runpage = app_page1
    st.session_state.runpage()
else:
    st.session_state.runpage = app_page2
    st.session_state.runpage()
