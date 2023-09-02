import streamlit as st

elastic_url = "https://localhost:9200"
elastic_ca_certs = "D:\\Games\\DnD\\Project\\ca.crt"
elastic_api_key = ("ZEp1VooB33IZbjn_Kxnq","KaiwoWUmTpWqSGrHq98ZNQ")

# queries Elastic for unfinished quests and returns array
from elasticsearch import Elasticsearch

# creates Elastic connection
client = Elasticsearch(
    elastic_url,
    ca_certs=elastic_ca_certs,
    api_key=elastic_api_key
)

response = client.index(index="test",document={"message":"this is a test"})

for line in response:
    print(line)

# close Elastic connection
client.close()