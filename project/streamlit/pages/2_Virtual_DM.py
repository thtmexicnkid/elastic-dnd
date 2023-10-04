# Elastic D&D
# Author: thtmexicnkid
# Last Updated: 10/04/2023
# 
# Streamlit - Virtual DM Page - Allows the user to ask questions and receive answers automatically.

import streamlit as st
from functions import *
from variables import *

# displays application title and sets page accordingly
display_image(streamlit_data_path + "banner.png")

# initializes session state, loads login authentication configuration, and performs index/data view setup in Elastic
initialize_session_state(["username"])
config, authenticator = load_yml()

# makes user log on to view page
if not st.session_state.username:
    error_message("UNAUTHORIZED: Please login on the Home page.",False)
else:
    st.header('Virtual DM',divider=True)
    st.session_state["log_index"] = "dnd-notes-" + st.session_state.username
    virtual_dm_variable_list = ["question","response","question_vector","query_results","answer","answer_vector","log_payload"]
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    st.session_state["question"] = st.chat_input("Ask the Virtual DM a question")
    if st.session_state.question:
        st.session_state["question"] = text_cleanup(st.session_state.question)
        # Display user message in chat message container
        st.chat_message("user").markdown(st.session_state.question)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": st.session_state.question})
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            # gets vector object for use with AI functionality
            st.session_state["question_vector"] = api_get_vector_object(st.session_state.question)
            if st.session_state.question_vector == None:
                error_message("AI API vectorization failure",2)
            else:
                st.session_state["query_results"] = elastic_ai_notes_query(st.session_state.question_vector)
                st.session_state["answers"] = api_get_question_answer(st.session_state.question,st.session_state.query_results)
                for answer in st.session_state.answers:
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.session_state["answer_vector"] = api_get_vector_object(answer)
                    if st.session_state.answer_vector == None:
                        error_message("AI API vectorization failure",2)
                    else:
                        st.session_state["log_payload"] = json.dumps({"question":st.session_state.question,"question_vector":st.session_state.question_vector,"answer":answer,"answer_vector":st.session_state.answer_vector})
                        elastic_index_document("virtual_dm-questions_answers",st.session_state.log_payload,False)

    clear_session_state(virtual_dm_variable_list)
