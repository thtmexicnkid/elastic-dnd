# Elastic D&D
# Author: thtmexicnkid
# Last Updated: 09/12/2023
# 
# Streamlit app that allows for D&D note-taking into Elastic by text or audio.

import streamlit as st
import streamlit_authenticator as stauth

### VARIABLES ###
# *** change this to fit your environment ***
assemblyai_api_key = "API_KEY"
elastic_api_key = "API_KEY"

# *** DO NOT CHANGE ***
elastic_url = "https://es01:9200"
elastic_ca_certs = "certs/ca/ca.crt"
kibana_url = "http://kibana:5601"
streamlit_data_path = "data/"
streamlit_project_path = "streamlit/"

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

def app_page2():
    st.session_state["log_index"] = "dnd-notes-" + st.session_state.username
    # displays note input, virtual DM, and account widgets
    tab1, tab2, tab3 = st.tabs(["Note Input", "WIP - Ask Virtual DM", "Account"])
    # note input tab
    with tab1:
        st.session_state["note_type"] = st.selectbox("Audio or Text?", ["Audio","Text"], index=0)
        # runs app_page2_* functions depending on what is selected in selectbox
        if st.session_state.note_type == "Audio":
            st.session_state.runpage = app_page2_audio
            st.session_state.runpage()
        elif st.session_state.note_type == "Text":
            st.session_state.runpage = app_page2_text
            st.session_state.runpage()
        else:
            pass
    # virtual DM tab
    with tab2:
        #I want to run notes through AI to be able to ask questions from this tab and receive answers
        pass
    # Account tab
    with tab3:
        # runs app_page2_password_reset function
        st.session_state.runpage = app_page2_password_reset
        st.session_state.runpage()
        # logout button
        authenticator.logout('Logout', 'main')
    
def app_page2_audio():
    # displays audio note form and widgets
    import json
    
    #list of variables to clear from session state once finished
    audio_form_variable_list = ["log_type","log_session","file","submitted","transcribed_text","log_payload"]
    
    # displays note form widgets, creates note payload, sends payload to an Elastic index, and handles error / success / warning messages
    with st.form("audio_form", clear_on_submit=True):
        st.session_state["log_type"] = "audio"
        st.session_state["log_session"] = st.slider("Which session is this?", 0, 250)
        st.session_state["file"] = st.file_uploader("Choose audio file",type=[".3ga",".8svx",".aac",".ac3",".aif",".aiff",".alac",".amr",".ape",".au",".dss",".flac",".flv",".m2ts",".m4a",".m4b",".m4p",".m4p",".m4r",".m4v",".mogg",".mov",".mp2",".mp3",".mp4",".mpga",".mts",".mxf",".oga",".ogg",".opus",".qcp",".ts",".tta",".voc",".wav",".webm",".wma",".wv"])
        st.session_state["submitted"] = st.form_submit_button("Upload file")
        if st.session_state.submitted and st.session_state.file is not None:
            st.session_state["transcribed_text"] = transcribe_audio(st.session_state.file)
            if st.session_state.transcribed_text is not None:
                st.session_state["log_payload"] = json.dumps({"session":st.session_state.log_session,"type":st.session_state.log_type,"message":st.session_state.transcribed_text})
                elastic_index_document("dnd-notes-transcribed",st.session_state.log_payload)
            else:
                error_message("Audio transcription failure")
        else:
            st.warning('Please upload a file and submit')
    
    # clears session state
    clear_session_state(audio_form_variable_list)

def app_page2_password_reset():
    try:
        if authenticator.reset_password(st.session_state.username, 'Reset password'):
            success_message('Password modified successfully')
            update_yml()
    except Exception as e:
        error_message(e)

def app_page2_text():
    # displays text note form and widgets
    import json
    
    #list of variables to clear from session state once finished
    text_form_variable_list = ["log_type","log_session","note_taker","log_index","quest_type","quest_name","quest_finished","log_message","submitted","log_payload"]

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
                st.session_state["log_message"] = st.text_input("Input note text:")
                st.session_state["submitted"] = st.form_submit_button("Upload note")
                if st.session_state.submitted == True and st.session_state.log_message is not None:
                    st.session_state["log_payload"] = json.dumps({"finished":st.session_state.quest_finished,"message":st.session_state.log_message,"name":st.session_state.quest_name,"session":st.session_state.log_session,"type":st.session_state.log_type})
                    elastic_index_document(st.session_state.log_index,st.session_state.log_payload)
                    st.experimental_rerun()
                else:
                    st.warning('Please input note text and submit')
        else:
            quest_names = elastic_get_quests()
            with st.form("text_form_existing_quest", clear_on_submit=True):
                st.session_state["log_session"] = st.slider("Which session is this?", 0, 250)
                st.session_state["quest_name"] = st.selectbox("Which quest are you updating?", quest_names)
                st.session_state["quest_finished"] = st.checkbox("Did you finish the quest?")
                st.session_state["log_message"] = st.text_input("Input note text:")
                st.session_state["submitted"] = st.form_submit_button("Upload note")
                if st.session_state.submitted == True and st.session_state.log_message is not None:
                    # updates previous quest records to finished: true
                    if st.session_state.quest_finished == True:
                        elastic_update_quest_status(st.session_state.quest_name)
                    else:
                        pass
                    st.session_state["log_payload"] = json.dumps({"finished":st.session_state.quest_finished,"message":st.session_state.log_message,"name":st.session_state.quest_name,"session":st.session_state.log_session,"type":st.session_state.log_type})
                    elastic_index_document(st.session_state.log_index,st.session_state.log_payload)
                    st.experimental_rerun()
                else:
                    st.warning('Please input note text and submit')
    # displays note form for all other log types
    else:
        with st.form("text_form_wo_quest", clear_on_submit=True):
            st.session_state["log_session"] = st.number_input("Which session is this?", 0, 250)
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

def elastic_get_quests():
    # queries Elastic for unfinished quests and returns array
    from elasticsearch import Elasticsearch
    
    quest_names = []
    
    # creates Elastic connection
    client = Elasticsearch(
        elastic_url,
        ca_certs=elastic_ca_certs,
        api_key=elastic_api_key
    )
    
    # gets unfinished quests
    response = client.search(index=st.session_state.log_index,size=0,query={"bool":{"must":[{"match":{"type.keyword":"quest"}}],"must_not":[{"match":{"finished":"true"}}]}},aggregations={"unfinished_quests":{"terms":{"field":"name.keyword"}}})
    
    for line in response["aggregations"]["unfinished_quests"]["buckets"]:
        quest_names.append(line["key"])
    
    return quest_names
    
    # close Elastic connection
    client.close()

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

def elastic_kibana_setup(yml_config):
    # creates empty placeholder indices and data views for each player, as well as for transcribed notes
    import requests
    from elasticsearch import Elasticsearch
    
    # builds list of index patterns and descriptive data view names from YAML configuration
    kibana_setup = {"dnd-notes-*":"All Notes","dnd-notes-transcribed":"Audio Transcription Notes"}
    for username in yml_config["credentials"]["usernames"]:
        index = "dnd-notes-" + username
        name = yml_config["credentials"]["usernames"][username]["name"] + "'s Notes"
        kibana_setup[index] = name
    
    # creates indices and data views from list
    for entry in kibana_setup:
        index = entry
        name = kibana_setup[entry]
        
        # creates Elastic connection
        client = Elasticsearch(
            elastic_url,
            ca_certs=elastic_ca_certs,
            api_key=elastic_api_key
        )
        
        # creates index if it does not already exist
        response = client.indices.exists(index=index)
        if response != True:
            try:
                client.indices.create(index=index)
            except:
                pass
        
        # close Elastic connection
        client.close()
        
        # check if data view already exists
        url = kibana_url + "/api/data_views/data_view/" + index
        auth = "ApiKey " + elastic_api_key
        headers = {"kbn-xsrf":"true","Authorization":auth}
        response = requests.get(url,headers=headers)
        # if data view doesn't exist, create it
        if response.status_code != 200:
            url = kibana_url + "/api/data_views/data_view"
            json = {"data_view":{"title":index,"name":name,"id":index}}
            response = requests.post(url,headers=headers,json=json)
            # could put some error message here, don't think I need to yet

def elastic_update_quest_status(quest_name):
    # queries Elastic for unfinished quests and returns array
    from elasticsearch import Elasticsearch
    
    # creates Elastic connection
    client = Elasticsearch(
        elastic_url,
        ca_certs=elastic_ca_certs,
        api_key=elastic_api_key
    )
    
    # gets unfinished quests
    query_response = client.search(index=st.session_state.log_index,size=10000,query={"bool":{"must":[{"match":{"name.keyword":quest_name}}],"must_not":[{"match":{"finished":"true"}}]}})
    
    for line in query_response["hits"]["hits"]:
        line_id = line["_id"]
        update_response = client.update(index="dnd-notes-corver_flickerspring",id=line_id,doc={"finished":st.session_state.quest_finished})
    
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
    
    with open(streamlit_project_path + "auth.yml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    
    return config, authenticator

def success_message(text):
    # displays success message
    import time
    
    success = st.success(text)
    time.sleep(1)
    success.empty()

def transcribe_audio(file):
    # transcribes an audio file to text
    import requests
    
    # get file url
    headers = {'authorization':assemblyai_api_key}
    response = requests.post('https://api.assemblyai.com/v2/upload',headers=headers,data=file)
    url = response.json()["upload_url"]
    # get transcribe id
    endpoint = "https://api.assemblyai.com/v2/transcript"
    json = {"audio_url":url}
    headers = {"authorization":assemblyai_api_key,"content-type":"application/json"}
    response = requests.post(endpoint, json=json, headers=headers)
    transcribe_id = response.json()['id']
    result = {}
    #polling
    while result.get("status") != "processing":
        # get text
        endpoint = f"https://api.assemblyai.com/v2/transcript/{transcribe_id}"
        headers = {"authorization":assemblyai_api_key}
        result = requests.get(endpoint, headers=headers).json()

    while result.get("status") != 'completed':
        # get text
        endpoint = f"https://api.assemblyai.com/v2/transcript/{transcribe_id}"
        headers = {"authorization":assemblyai_api_key}
        result = requests.get(endpoint, headers=headers).json()

    return result['text']

def update_yml():
    # updates login authentication configuration file
    import yaml

    with open(streamlit_project_path + "auth.yml", 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

### PROGRAM ###

# initializes session state, loads login authentication configuration, and performs index/data view setup in Elastic
initialize_session_state(["username"])
config, authenticator = load_yml()
elastic_kibana_setup(config)

# displays application title and sets page accordingly
display_image(streamlit_data_path + "banner.png")
if not st.session_state.username:
    st.session_state.runpage = app_page1
    st.session_state.runpage()
else:
    st.session_state.runpage = app_page2
    st.session_state.runpage()

st.session_state
