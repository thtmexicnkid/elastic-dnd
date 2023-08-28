import streamlit as st
import streamlit_authenticator as stauth

elastic_url = "https://localhost:9200"
elastic_ca_certs = "PATH_TO_ELASTIC_CA.crt"
elastic_api_key = ("API_KEY","API_KEY_VALUE")
streamlit_path = "PATH_THAT_CONTAINS_APP_SCRIPT"

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
        st.session_state["note_type"] = st.selectbox("Audio or Text?", ["Audio","Text"], index=0)
        
        if st.session_state.note_type == "Audio":
            st.session_state.runpage = app_page2_audio
            st.session_state.runpage()
            if st.session_state == {}:
                st.session_state.runpage = app_page2_audio
                st.experimental_rerun()
        elif st.session_state.note_type == "Text":
            st.session_state.runpage = app_page2_text
            st.session_state.runpage()
            if st.session_state == {}:
                st.session_state.runpage = app_page2_text
                st.experimental_rerun()
        else:
            pass
    with tab2:
        #I want to run notes through AI to be able to ask questions from this tab and receive answers
        pass
    
    authenticator.logout('Logout', 'main')
    
def app_page2_audio():
    import json
    
    audio_form_variable_list = ["log_index","log_type","log_session","file","submitted","transcribed_text","log_payload"]
    
    with st.form("audio_form", clear_on_submit=True):
        st.session_state["log_index"] = "dnd-notes-transcribed"
        st.session_state["log_type"] = "audio"
        st.session_state["log_session"] = st.slider("Which session is this?", 0, 250)
        st.session_state["file"] = st.file_uploader("Choose audio file",type=["mp3"])
        st.session_state["submitted"] = st.form_submit_button("Upload file")

        if st.session_state.submitted and st.session_state.file is not None:
            #st.session_state["transcribed_text"] = transcribe_audio(st.session_state.file.name)
            st.session_state["transcribed_text"] = "Test"
            if st.session_state.transcribed_text is not None:
                st.session_state["log_payload"] = json.dumps({"session":st.session_state.log_session,"type":st.session_state.log_type,"message":st.session_state.transcribed_text})
                elastic_index_document(st.session_state.log_index,st.session_state.log_payload)
            else:
                st.error("Audio transcription failure")
        else:
            st.warning('Please upload a file and submit')
    
    clear_session_state(audio_form_variable_list)
    
def app_page2_text():
    import json
    #WIP
    text_form_variable_list = []
    """
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
    """

def clear_session_state(variable_list):
    for variable in variable_list:
        try:
            del st.session_state[variable]
        except:
            pass

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

def initialize_session_state(variable_list):
    for variable in variable_list:
        if variable not in st.session_state:
            st.session_state[variable] = None

def load_yml():
    import yaml
    from yaml.loader import SafeLoader
    
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
    
    assemblyai.settings.api_key = "ASSEMLY_AI_API_KEY"
    transcriber = assemblyai.Transcriber()
    transcript = transcriber.transcribe(streamlit_path + file)
    
    return transcript.text

def update_yml():
    import yaml
    
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