import json
import requests
import streamlit

elastic_url = "" + index + "/_doc"
elastic_headers = {"Content-Type":"application/json"}
elastic_auth = HTTPBasicAuth("ApiKey","")

def send_to_elastic(payload):
    response = requests.post(elastic_url,data=payload,headers=elastic_headers,auth=elastic_auth)
    return response.json

streamlit.title("D&D Note Input")
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

streamlit.button("Click to submit note.", on_click=send_to_elastic(json))
