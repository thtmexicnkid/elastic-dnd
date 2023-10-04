# Elastic D&D
# Author: thtmexicnkid
# Last Updated: 10/04/2023
# 
# Streamlit - Backend - Houses all functions used in pages of the application.

import json
import requests
import streamlit as st
import streamlit_authenticator as stauth
import time
import yaml
from elasticsearch import Elasticsearch
from PIL import Image
from variables import *
from yaml.loader import SafeLoader

### FUNCTIONS ###
def api_get_question_answer(question,query_results):
    # returns an answer to a question asked to virtual DM
    
    fastapi_endpoint = "/get_question_answer/"
    full_url = fastapi_url + fastapi_endpoint + question + "/" + query_results
    response = requests.get(full_url)
    
    try:
        answer = response.json()
    except:
        answer = None
        print(response.content)

    return answer
    
def api_get_vector_object(text):
    # returns vector object from supplied text
    
    fastapi_endpoint = "/get_vector_object/"
    full_url = fastapi_url + fastapi_endpoint + text
    response = requests.get(full_url)
    
    try:
        message_vector = response.json()
    except:
        message_vector = None
        print(response.content)
    
    return message_vector

def text_cleanup(text):
    punctuation = ["/", "?"]
    for symbol in punctuation:
        text = text.replace(symbol," ")
    
    return text

def clear_session_state(variable_list):
    # deletes variables from streamlit session state
    for variable in variable_list:
        try:
            del st.session_state[variable]
        except:
            pass

def display_image(image_path):
    # displays an image via path relative to streamlit app script
    image = Image.open(image_path)
    st.image(image)

def elastic_ai_notes_query(vector_object):
    # queries Elastic via a KNN query to return answers to questions via virtual DM
    
    # creates Elastic connection
    client = Elasticsearch(
        elastic_url,
        ca_certs=elastic_ca_certs,
        api_key=elastic_api_key
    )
    
    # sends document to index with success or failure message
    response = client.search(index="dnd-notes-*",knn={"field":"message_vector","query_vector":vector_object,"k":10,"num_candidates":100})
    
    return response['hits']['hits'][0]['_source']["message"]
    
    # close Elastic connection
    client.close()

def elastic_get_quests():
    # queries Elastic for unfinished quests and returns array    
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

def elastic_index_document(index,document,status_message):
    # sends a document to an Elastic index
    
    # creates Elastic connection
    client = Elasticsearch(
        elastic_url,
        ca_certs=elastic_ca_certs,
        api_key=elastic_api_key
    )
    
    # sends document to index with success or failure message
    response = client.index(index=index,document=document)
    
    if status_message == True:
        if response["result"] == "created":
            success_message("Note creation successful")
        else:
            error_message("Note creation failure",2)
    else:
        pass
    
    # close Elastic connection
    client.close()

def elastic_kibana_setup(yml_config):
    # creates empty placeholder indices and data views for each player, as well as for transcribed notes
    
    # builds list of index patterns and descriptive data view names from YAML configuration
    kibana_setup = {"dnd-notes-*":"All Notes","dnd-notes-transcribed":"Audio Transcription Notes","virtual_dm-questions_answers":"Virtual DM Notes"}
    for username in yml_config["credentials"]["usernames"]:
        index = "dnd-notes-" + username
        name = yml_config["credentials"]["usernames"][username]["name"] + "'s Notes"
        kibana_setup[index] = name
    
    # creates indices and data views from usernames
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
            json = {"data_view":{"title":index,"name":name,"id":index,"timeFieldName":"@timestamp"}}
            response = requests.post(url,headers=headers,json=json)
            # could put some error message here, don't think I need to yet

def elastic_update_quest_status(quest_name):
    # queries Elastic for unfinished quests and returns array
    
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

def error_message(text,timeframe):
    # displays error message    
    error = st.error(text)
    
    if timeframe == False:
        pass
    else:
        time.sleep(seconds)
        error.empty()

def initialize_session_state(variable_list):
    # creates empty variables in streamlit session state
    for variable in variable_list:
        if variable not in st.session_state:
            st.session_state[variable] = None

def load_yml():
    # loads login authentication configuration    
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
    success = st.success(text)
    time.sleep(2)
    success.empty()

def transcribe_audio(file):
    # transcribes an audio file to text

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
    with open(streamlit_project_path + "auth.yml", 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
