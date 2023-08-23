# thtmexicnkid
# Streamlit: D&D Note Input
# Author: Joe Munoz
# Last Updated: Aug 22nd, 2023
# 
# Creates GUI for note input for D&D via Elastic

### Modules
import json
import streamlit
from elasticsearch import Elasticsearch

### Static variables
elastic_url = "https://localhost:9200"
elastic_ca_certs = "PATH_TO_CA.crt"
elastic_api_key = ("API_KEY_ID","API_KEY_VALUE")

### Functions
def send_to_elastic(index,document):
    # Connect to Elasticsearch
    client = Elasticsearch(
        elastic_url,
        ca_certs=elastic_ca_certs,
        api_key=elastic_api_key
    )
    
    response = client.index(index=index,document=document)
    print(response)

### Program
streamlit.title("D&D Note Input")

# Allows for note sorting based on who is taking the note. Variables are set accordingly.
note_taker = streamlit.selectbox("Who are you?", ["Bengamin Bolton","Corver Flickerspring","Mae Avraya", "Nyx", "Tanja"])
if note_taker == "Bengamin Bolton":
    index = "dnd-notes-bengamin_bolton"
elif note_taker == "Corver Flickerspring":
    index = "dnd-notes-corver_flickerspring"
elif note_taker == "Mae Avraya":
    index = "dnd-notes-mae_avraya"
elif note_taker == "Nyx":
    index = "dnd-notes-nyx"
elif note_taker == "Tanja":
    index = "dnd-notes-tanja"

# Setting dynamic variables based on user input. Payload is populated accordingly.
type = streamlit.selectbox("What kind of note is this?", ["location","overview","person","quest"])
session = streamlit.number_input("Which session is this?", 0, 250)
message = streamlit.text_input("Input note here:")
if type == "quest":
    #query elastic for a list of quest names???
    name = streamlit.text_input("What is the name of the quest?")
    finished = streamlit.checkbox("Is the quest finished?")

    json = json.dumps({"finished":finished,"message":message,"name":name,"session":session,"type":type})
else:
    json = json.dumps({"message":message,"session":session,"type":type})

# Sends the note to Elastic.
streamlit.button("Click to submit note.",on_click=send_to_elastic, args=[index,json])
