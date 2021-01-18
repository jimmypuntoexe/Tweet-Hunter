import tweepy
import json
import os
from setup.config import CONSUMER_KEY, CONSUMER_SECRET, USER
import pandas as pd
from json.decoder import JSONDecodeError
import re




def process_tweet(tweet, id, topic):
    temp_tweet = {}
    temp_tweet["id"] = id
    temp_tweet["tweet_id"] = tweet.id_str
    temp_tweet["created_at"] = tweet.created_at.isoformat()
    temp_tweet["text"] = tweet.full_text
    temp_tweet["truncated"] = tweet.truncated
    temp_tweet["user_name"] = tweet.user.name
    temp_tweet["followers_count"] = int(tweet.user.followers_count)
    temp_tweet["like"] = int(tweet.favorite_count)
    temp_tweet["retweet"] = int(tweet.retweet_count)
    temp_tweet["profile_image_url"] = tweet.user.profile_image_url_https
    temp_tweet["tweet_url"] = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
    temp_tweet["hashtags"] = re.findall(r"#(\w+)", tweet.full_text)
    if tweet.place is not None:
        temp_tweet["country"] = tweet.place.country_code
    else:
        temp_tweet["country"] = ""

    temp_tweet["topic"] = topic.split()[0]

    return temp_tweet

def find_last_id(tweets):

    since_id = {}

    df = pd.DataFrame([tweet for tweet in tweets])
    df = df[["tweet_id", "created_at", "topic"]]

    df = df.sort_values("created_at").groupby("topic").last()
    max_id = max(df["tweet_id"].tolist())

    return max_id


def download_tweets_by_topic(topic, id_tweet, sinceId):
    tweets = []
    max_id = -1
    id_tweet = id_tweet
    tweetCount = 0
    if sinceId != {}:
        sinceId = str(sinceId)
    else:
        sinceId = "0"
    while tweetCount < total_tweets:
            try:
                if (max_id <= 0):
                    if (sinceId=='0'):
                        new_tweets =  api.search(
                        q=topic,
                        count=tweet_per_query,
                        tweet_mode="extended",
                        lang="en",
                        result_type="mixed",
                        include_entities=False,
                    )
                    else:
                        new_tweets = api.search(
                        q=topic,
                        count=tweet_per_query,
                        tweet_mode="extended",
                        lang="en",
                        result_type="mixed",
                        include_entities=False,
                        since_id=sinceId)
                else:
                    if (sinceId=='0'):
                        new_tweets = api.search(
                        q=topic,
                        count=tweet_per_query,
                        tweet_mode="extended",
                        lang="en",
                        result_type="mixed",
                        include_entities=False,
                        max_id=str(max_id - 1))
                    else:
                        new_tweets = api.search(
                        q=topic,
                        count=tweet_per_query,
                        tweet_mode="extended",
                        lang="en",
                        result_type="mixed",
                        include_entities=False,
                        max_id=str(max_id - 1),
                        since_id=sinceId)
                if not new_tweets:
                    print("No more tweets found")
                    break
                for tweet in new_tweets:
                    tweets.append(process_tweet(tweet, id_tweet, topic))
                    id_tweet = id_tweet + 1
                    
                print(tweetCount)
                tweetCount += len(new_tweets)
                max_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                # Just exit if any error
                print("some error : " + str(e))
                break
            print ("Downloaded {0} tweets for topic", topic)
    return tweets, id_tweet 
    
def read_tweet(filepath):
    with open(filepath) as json_file:
         data = json.load(json_file)
    return data          
                 
    

if __name__ == "__main__":


    CONSUMER_KEY = "MuCbGgnCjkUkjWSxwVVYETnfH"
    CONSUMER_SECRET = "WOVIxFRnqrhgmqC8qtsp8FPDdjqtW114PfvCLl51BFKat3IIVf"
    ACCESS_TOKEN = "1335961605113307136-eFFNXO7aT4vxxneCAltb8SCZ7rrVVo"
    ACCESS_TOKEN_SECRET = "tln7UwKWOUgLr8rP62jNxsY3TN66tph2ZUzzI39vRZKfB"

    auth = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


    total_tweets= 150000
    tweet_per_query = 100  
    topic_file = os.path.join("repository", "topic_tweets", "topics.json")
    tweets = read_tweet(topic_file)
  
    print(len(tweets))
    if len(tweets) == 0:
        id_tweet = 1
        tweets = []
        since_id = {}
    else:
        id_tweet = tweets[len(tweets) - 1]["id"]
        since_id = find_last_id(tweets=tweets)
    topics = [
        "sport -filter:retweets",
        "music -filter:retweets",
        "cinema -filter:retweets",
        "technology -filter:retweets"
    ]

    for topic in topics:
        print("Download tweets... for ", topic)
        temp_list, last_id = download_tweets_by_topic(
            topic=topic, id_tweet=id_tweet, sinceId=since_id
        )
        id_tweet = last_id
        print(len(temp_list), " for", topic)
        tweets.extend(temp_list)

    print("Ora nella lista ci sono: ", len(tweets), " tweets")

    with open(topic_file, "w") as outfile:
        json.dump(tweets, outfile, indent=3)