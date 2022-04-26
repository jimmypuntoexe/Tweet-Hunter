# README
Project A: Personalized Search Engine for microblog  

* Gianmaria Balducci, 807141


## Requirements


* Download and install [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/install/)
* Download and install python-venv with `sudo apt-get install -y python3-venv` 


## Installation

* download data folder [data](https://drive.google.com/drive/folders/13USdM3Ts2ZYb1S3mfct6OFxseFivPnCX?usp=sharing)    
* put folders models and repository in RetrivalProject directory
* extract the zip folder
* `cd RetrivalProject`
* install requirements `pip install -r requirements.txt
* activate environment with `source bin/activate`
`



## Usage
* linux kibana start`sudo sysctl -w vm.max_map_count=262144`
* start services `docker-compose up -d`
* create index `python index/indexing.py`
* run the web app `python webapp/app.py`

Index can be managed at http://localhost:5601/app/kibana.  
Web app is at http://127.0.0.1:5000/.

## My Workflow

1. `python retrive_tweets/download_tweets_topics`
2. `python retrive_tweets/download_tweets`
3. `python preprocess/preprocessing.py` 
4. `python word_embeddings/embeddings` 
5. `python index/indexing.py`
6. `python webapp/app.py` browse http://127.0.0.1:5000/
