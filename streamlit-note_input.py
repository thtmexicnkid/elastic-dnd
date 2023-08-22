import streamlit

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
#streamlit.text(index)

type = streamlit.selectbox("What kind of note is this?", ["location","overview","person","quest"])
session = streamlit.number_input("Which session is this?", 0, 250)
message = streamlit.text_input("Input note here:")
if type == "quest":
    name = streamlit.text_input("What is the name of the quest?")
    finished = streamlit.checkbox("Is the quest finished?")
    streamlit.write([index, type, session, message, name, finished])
streamlit.write([index, type, session, message])
