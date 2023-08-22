import streamlit

streamlit.title("D&D Note Input")
note_taker = streamlit.selectbox('Who are you?', ['Bengamin Bolton','Corver Flickerspring','Mae Avraya', 'Nyx', 'Tanja'])

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

streamlit.text(index)
