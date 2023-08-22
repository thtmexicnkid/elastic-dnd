import streamlit

streamlit.title("D&D Note Input")
note_taker = streamlit.selectbox('Who are you?', ['Bengamin Bolton','Corver Flickerspring','Mae Avraya', 'Nyx', 'Tanja'])

if note_taker == "Bengamin Bolton":
  index = "dnd-notes-bengamin_bolton"
  streamlit.text(index)
