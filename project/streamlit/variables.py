# Elastic D&D
# Author: thtmexicnkid
# Last Updated: 11/03/2023
# 
# Streamlit - Backend - Houses variables that are loaded into pages of the application.

### VARIABLES ###
# *** change this to fit your environment ***
# use this is using free method for audio transcription
assemblyai_api_key = None
# use this is paying for AssemblyAI for audio transcription
#assemblyai_api_key = "API_KEY"
elastic_api_key = "API_KEY"

# *** DO NOT CHANGE ***
elastic_url = "https://es01:9200"
elastic_ca_certs = "certs/ca/ca.crt"
fastapi_url = "http://api:8000"
kibana_url = "http://kibana:5601"
streamlit_data_path = "data/"
streamlit_project_path = "streamlit/"
