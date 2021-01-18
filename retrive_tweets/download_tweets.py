import tweepy
import os
import json
import sys
from setup.config import CONSUMER_KEY, CONSUMER_SECRET, USER


def save_user_tweets(user, tweets):
    with open(os.path.join("repository", "users_tweets", user + ".json"), "w") as outfile:
        json.dump(tweets, outfile, indent=3)

def download_tweets_by_user(user, count= 200):

    alltweets = []
    tweets = {}
    old_tweet = {}  
    
    new_tweets = api.user_timeline(
            screen_name=user,
            count=count,
            tweet_mode="extended",
            include_entities=False,
        )
    
    
    alltweets.extend(new_tweets)
    oldest = alltweets[-1].id - 1
    
    while len(new_tweets) > 0:
        new_tweets = api.user_timeline( screen_name=user,
            count=count,
            tweet_mode="extended",
            include_entities=False,
            max_id=oldest)

        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id - 1
        
        print(f"...{len(alltweets)} tweets downloaded so far")
    for tweet in alltweets:
        if hasattr(tweet, "retweeted_status"):
            tweets[tweet.id_str] = tweet.retweeted_status.full_text
        else:
            tweets[tweet.id_str] = tweet.full_text

    tot_tweets = {**tweets, **old_tweet}

    return tot_tweets

if __name__ == "__main__":
    auth = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    
    tweets = {}
    print(USER)
    for user in USER:
        tweets = download_tweets_by_user(user, 200)
        save_user_tweets(user, tweets)
    print("Tweet totali ", len(tweets))
