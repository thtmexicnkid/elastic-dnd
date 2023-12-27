# Elastic D&D
# Author: thtmexicnkid
# Last Updated: 12/27/2023
# 
# Streamlit - Backend - Houses all functions used in pages of the application.

import json
import nltk
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

def clear_session_state(variable_list):
    # deletes variables from streamlit session state
    for variable in variable_list:
        try:
            del st.session_state[variable]
        except:
            pass

def display_image(image_path,column_width_selector):
    # displays an image via path relative to streamlit app script
    image = Image.open(image_path)
    st.image(image,use_column_width=column_width_selector)

def elastic_ai_notes_query(vector_object):
    # queries Elastic via a KNN query to return answers to questions via virtual DM
    
    # creates Elastic connection
    client = Elasticsearch(
        elastic_url,
        ca_certs=elastic_ca_certs,
        api_key=elastic_api_key
    )
    
    # sends document to index with success or failure message
    response = client.search(index="dnd-notes-*",knn={"field":"content_vector","query_vector":vector_object,"k":10,"num_candidates":100})
    
    return response["hits"]["hits"][0]["_source"]["message"]
    
    # close Elastic connection
    client.close()

def elastic_get_previous_session_summary(log_index):
    # creates Elastic connection
    client = Elasticsearch(
        elastic_url,
        ca_certs=elastic_ca_certs,
        api_key=elastic_api_key
    )

    # gets overview note from last session
    response = client.search(index=log_index,size=1,sort=["session:desc"],source=["message"],query={"bool":{"must":[{"match":{"type":"overview"}}]}})
    
    return response["hits"]["hits"][0]["_source"]["message"]

def elastic_get_quests(log_index):
    # queries Elastic for unfinished quests and returns array    
    quest_names = []
    
    # creates Elastic connection
    client = Elasticsearch(
        elastic_url,
        ca_certs=elastic_ca_certs,
        api_key=elastic_api_key
    )
    
    # gets unfinished quests
    response = client.search(index=log_index,size=0,query={"bool":{"must":[{"match":{"type":"quest"}}],"must_not":[{"match":{"quest.finished":"true"}}]}},aggregations={"unfinished_quests":{"terms":{"field":"quest.name.keyword"}}})
    
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

def error_message(text,seconds):
    # displays error message    
    error = st.error(text)
    
    if seconds == False:
        pass
    else:
        time.sleep(seconds)
        error.empty()

def generate_unique_id():
    # generate id that will tie all text chunks together
    import uuid
    
    unique_id = str(uuid.uuid4())
    
    return unique_id

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

def split_text_with_overlap(text, chunk_size=500, overlap_size=100):
    # download punky and initialize tokenizer
    nltk.download("punkt")
    tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()

    # separate text into an array of sentences
    array = tokenizer.tokenize(text)

    # if length of text chunk > 500, index document
    # afterwards, prepend previous 100 characters for context overlap
    chunks = []
    chunk = ""
    for index, sentence in enumerate(array):
        if (len(chunk) + len(sentence)) >= chunk_size:
            chunks.append(chunk)

            overlap = ""
            overlap_length = len(overlap)
            overlap_index = index - 1
            while ((overlap_length + len(array[overlap_index])) < overlap_size) and overlap_index != -1:
                overlap = (array[overlap_index] + overlap)
                overlap_length = len(overlap)
                overlap_index = overlap_index - 1
            chunk = overlap + sentence
        else:
            chunk += sentence
    # index last bit of text that may not hit length limit
    chunks.append(chunk)
    
    return chunks

def success_message(text):
    # displays success message
    success = st.success(text)
    time.sleep(2)
    success.empty()

def transcribe_audio_free(file_object):
    # transcribes an audio file to text via OpenAI Whisper
    import os
    import shutil
    import speech_recognition as sr
    from pydub import AudioSegment
    from pydub.silence import split_on_silence
    from tempfile import NamedTemporaryFile
    
    # get extension
    filename, file_extension = os.path.splitext(file_object.name)
    
    # create temp file
    with NamedTemporaryFile(suffix=file_extension,delete=False) as temp:
        temp.write(file_object.getvalue())
        temp.seek(0)

        # split file into chunks
        audio = AudioSegment.from_file(temp.name)
        audio_chunks = split_on_silence(audio,
            # experiment with this value for your target audio file
            min_silence_len=3000,
            # adjust this per requirement
            silence_thresh=audio.dBFS-30,
            # keep the silence for 1 second, adjustable as well
            keep_silence=100,
        )
        
        # create a directory to store the audio chunks
        folder_name = "audio-chunks"
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        whole_text = ""
        
        # process each chunk 
        for i, audio_chunk in enumerate(audio_chunks, start=1):
            # export audio chunk and save it in the `folder_name` directory.
            chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
            audio_chunk.export(chunk_filename, format="wav")
            # recognize the chunk
            try:
                # audio to text
                r = sr.Recognizer()
                uploaded_chunk = sr.AudioFile(chunk_filename)
                with uploaded_chunk as source:
                    chunk_audio = r.record(source)
                text = r.recognize_whisper(chunk_audio,"medium")
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = f"{text.capitalize()}. "
                print(chunk_filename, ":", text)
                whole_text += text

        # close temp file
        temp.close()
        os.unlink(temp.name)
        
    # clean up the audio-chunks folders
    shutil.rmtree(folder_name)
    
    # return the text for all chunks detected
    return whole_text

def transcribe_audio_paid(file):
    # transcribes an audio file to text via AssemblyAI

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

def text_cleanup(text):
    # removes punctuation incompatible with data vectorization API
    punctuation = ["/", "?"]
    for symbol in punctuation:
        text = text.replace(symbol," ")
    
    return text

def update_yml(updated_config):
    # updates login authentication configuration file
    with open(streamlit_project_path + "auth.yml", 'w') as file:
        yaml.dump(updated_config, file, default_flow_style=False)
