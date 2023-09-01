![elastic-dnd banner](https://github.com/thtmexicnkid/elastic-dnd/blob/main/banner.png)

# Description
My attempt at using Elastic while playing Dungeons &amp; Dragons; mainly for note-taking, but also for anything else that comes to mind.

# Application Functions
* Login + Password system for access control
* Manual note input with a handful of types -- location, quest, person, overview
* Audio to text transcription from recorded session audio
* WORK IN PROGRESS -- Ask the Virtual DM questions about your sessions

# Dependencies
* Some sort of Python environment. I set mine up via [Anaconda](https://docs.anaconda.com/free/anaconda/install/).
  * Modules:
    * [Python - Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/index.html)
    * [Python - Streamlit Authenticator](https://github.com/mkhorasani/Streamlit-Authenticator)
    * [Python - Streamlit](https://docs.streamlit.io/library/get-started/installation)
* Some sort of Elastic environment:
  * [Elastic Cloud](https://www.elastic.co/guide/en/cloud/current/ec-create-deployment.html)
  * Standalone:
    * [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/setup.html)
    * [Kibana](https://www.elastic.co/guide/en/kibana/current/setup.html)
* An [AssemblyAI](https://www.assemblyai.com/) API key for audio transcription
