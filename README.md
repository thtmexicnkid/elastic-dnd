![elastic-dnd banner](https://github.com/thtmexicnkid/elastic-dnd/blob/main/data/banner.png)

# Description
My attempt at using Elastic while playing Dungeons &amp; Dragons; mainly for note-taking, but also for anything else that comes to mind.

# Application Functions
* Login + Password system for access control
* Manual note input with a handful of types -- location, quest, person, overview
* Audio to text transcription from recorded session audio
* WORK IN PROGRESS -- Ask the Virtual DM questions about your sessions

# Dependencies
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) or [Docker Engine](https://docs.docker.com/engine/install/) with [Docker-Compose](https://docs.docker.com/compose/install/)
  * Docker Desktop comes with Docker-Compose installed already; definitely the easier option.
* An [AssemblyAI](https://www.assemblyai.com/) API key for audio transcription

# Setup
### Docker Setup
* Download or clone elastic-dnd repo to whatever directory/folder you want this to run from
* Edit ".env" file and make the following changes:
  * Change ELASTIC_PASSWORD and KIBANA_PASSWORD to something you'll remember
  * Set ES_MEM_LIMIT and KB_MEM_LIMIT to a value (in bytes) reflecting what is available in your environment
    * NOTE -- I have 32GB available and set mine to 8GB a piece. Truthfully, for a deployment this size, that is overkill. You would probably be okay with a 2-4GB a piece.
* Open command prompt / terminal and navigate to folder containing "docker-compose.yml"
* Run "docker-compose up" and wait for your deployment to create itself

### Streamlit Setup
* Log into [Kibana](http://localhost:5601):
  * Username is "elastic"
  * Password is whatever you set in the .env file
* Navigate to [Dev Tools](http://localhost:5601/app/dev_tools) and run the following:
```
PUT _security/api_key
{
  "name": "streamlit-auth"
}
```
* Paste the "id" and "api_key" values into the respective variables in "projects/app.py"
* Paste your AssemblyAI API key into the "transcribe_audio" function in "projects/app.py"

### Player Setup
* Either (you can read more about this on my [blog](https://dev.to/thtmexicnkid/elastic-dd-week-2-streamlit-the-login-page-4olh)):
  * add users to "projects/auth.yml" manually ***OR***
  * add player emails to the "preauthorized" section of "projects/auth.yml" and let them use the register function of the Streamlit application
    * Navigate to the [Streamlit application](http://localhost:8501) and use the Register tab:
* In "project/app.py", edit the "username_to_index" variable such that the username is associated with the backing note index.
  * {"player1":"dnd-notes-player1","player2":"dnd-notes-player2"}
* Have players create some notes!

### Kibana Setup
* If players have not created notes yet, place an empty index for each player:
  * Navigate to [Dev Tools](http://localhost:5601/app/dev_tools) and run the following, swapping out the index names for the ones you set up in the Streamlit application variable (***keep dnd-notes-transcribed***):
```
PUT dnd-notes-player1
PUT dnd-notes-player2
PUT dnd-notes-transcribed
```
* Navigate to [Data Views](http://localhost:5601/app/management/kibana/dataViews) and create one for each player, one for the audio transcription notes, and one to view all at the same time
  * Name: Player 1's Notes, Audio Transcription Notes, All Notes, etc.
  * Index Pattern: dnd-notes-player1, dnd-notes-transcribed, dnd-notes-*

# Viewing Your Notes
* Navigate to [Discover](http://localhost:5601/app/discover) -- select your Data View at the top left and your timeframe at the top right
* Check out this [documentation](https://www.elastic.co/guide/en/kibana/current/kuery-query.html) to learn how to search
