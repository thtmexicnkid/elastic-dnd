![elastic-dnd banner](https://github.com/thtmexicnkid/elastic-dnd/blob/main/data/banner.png)

# Description
My attempt at using Elastic while playing Dungeons &amp; Dragons; mainly for note-taking, but also for anything else that comes to mind.

 A blog is being updated weekly, showing code and implementation progress, how and why I am doing things, and issues I am having along the way. You can check that out [here](https://dev.to/thtmexicnkid)

# Application Functions
* Login + Password system for access control
* Manual note input with a handful of types -- location, quest, person, overview
* Audio to text transcription from recorded session audio
* Ask the Virtual DM questions about your sessions
* WORK IN PROGRESS -- User dashboard with last session info, outstanding quest info, etc.

# Dependencies
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) or [Docker Engine](https://docs.docker.com/engine/install/) with [Docker-Compose](https://docs.docker.com/compose/install/)
  * Docker Desktop comes with Docker-Compose installed already; definitely the easier option.
* An [OpenAI](https://platform.openai.com/) API key for Virtual DM functions
## Optional
* An [AssemblyAI](https://www.assemblyai.com/) API key for audio transcription (Much faster than the free method)

# Setup
### Docker Setup
* Download or clone elastic-dnd repo to whatever directory/folder you want this to run from
* Edit ".env" file and make the following changes:
  * Change ELASTIC_PASSWORD and KIBANA_PASSWORD to something you'll remember
  * Set ES_MEM_LIMIT and KB_MEM_LIMIT to a value (in bytes) reflecting what is available in your environment
    * NOTE -- I have 32GB available and set mine to 8GB a piece. Truthfully, for a deployment this size, that is overkill. You would probably be okay with a 2-4GB a piece.
* Open command prompt / terminal and navigate to folder containing the "docker-compose-*.yml" files.
* Rename either "docker-compose-linux.yml" or "docker-compose-windows.yml" to "docker-compose.yml", depending on which operating system you are running the program on.
* Run "docker-compose up" and wait for your deployment to create itself

> ***NOTE*** -- The libraries for the free audio transcription function take a little while to install.

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
* Paste the API key value into the "elastic_api_key variable" in "projects/app.py"
* Paste your AssemblyAI API key into the "transcribe_audio" function in "projects/app.py"

### Player Setup
* Either (you can read more about this on my [blog](https://dev.to/thtmexicnkid/elastic-dd-week-2-streamlit-the-login-page-4olh)):
  * add users to "projects/auth.yml" manually ***OR***
  * add player emails to the "preauthorized" section of "projects/auth.yml" and let them use the register function of the Streamlit application
    * Navigate to the [Streamlit application](http://localhost:8501) and use the Register tab:

# Viewing Your Notes
* Navigate to [Discover](http://localhost:5601/app/discover) -- select your Data View at the top left and your timeframe at the top right
* Check out this [documentation](https://www.elastic.co/guide/en/kibana/current/kuery-query.html) to learn how to search

# Accessing from the Internet
* Via your router, forward ports 5601 and 8501 to your machine. (I will talk about this in-depth on my October 6th, 2023 blog post.)
* Find your public IP address with [https://whatismyipaddress.com/](https://whatismyipaddress.com/)
* Connect to the applications:
  * Users on the same network as the hosted applications can use [http://localhost:5601](http://localhost:5601) and [http://localhost:8501](http://localhost:8501) for Kibana and Streamlit, respectively.
  * Users on networks external to the hosted applications can use [http://<PUBLIC_IP>:5601](http://<PUBLIC_IP>:5601) and [http://<PUBLIC_IP>:8501](http://<PUBLIC_IP>:8501) for Kibana and Streamlit, respectively.
