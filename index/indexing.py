import os
import json
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from index_config import mapping_index

es = Elasticsearch(hosts=["localhost"])
index_name = 'twindex'
index_config = mapping_index
body_path =  os.path.join("repository", "topic_tweets", "topics.json")

if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
    print('Index ', index_name, 'already exists....deleting')

res = es.indices.create(index=index_name, body= index_config, ignore= 400)

if "acknowledged" in res:
    if res["acknowledged"] == True:
        print("Indexing success:", res["index"])

elif "error" in res:
    print("ERROR:", res["error"]["root_cause"])
    print("TYPE:", res["error"]["type"])

        # print out the res:
print("\nresponse:", res)

with open(body_path) as json_file:
    tweets_topics = json.load(json_file)
tweets = tweets_topics

tweet_list = []
count = 0

for tweet in tweets:
    count += 1        #tweet_list.append(tweet)
    es.index(index=index_name,  body=tweet)
    print("Indexed ", count ,"tweets.")

        







       