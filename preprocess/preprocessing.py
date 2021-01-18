import re
import html
import os
import emoji
import nltk
import regex
import string
import json
import pickle
import pandas
import numpy as np
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize.casual import TweetTokenizer
import itertools
import collections
from collections import Counter
from setup.config import CONSUMER_KEY, CONSUMER_SECRET, USER

START_OF_LINE = r"^"
OPTIONAL = "?"
ANYTHING = "."
ZERO_OR_MORE = "*"
ONE_OR_MORE = "+"

SPACE = "\s"
SPACES = SPACE + ONE_OR_MORE
NOT_SPACE = "[^\s]" + ONE_OR_MORE
EVERYTHING_OR_NOTHING = ANYTHING + ZERO_OR_MORE

ERASE = ""
FORWARD_SLASH = "\/"
NEWLINES = r"[\r\n]"

RE_TWEET = START_OF_LINE + "RT" + SPACES

HYPERLINKS = ("http" + "s" + OPTIONAL + ":" + FORWARD_SLASH + FORWARD_SLASH
              + NOT_SPACE + NEWLINES + ZERO_OR_MORE)

HASH = "#"



def read_tweet(filepath):
    with open(filepath) as json_file:
         data = json.load(json_file)
    return data 


def save_user_tweets(user, tweets):
    with open(os.path.join("repository", "users_tweets", user + "_cleaned.json"), "w") as outfile:
        json.dump(tweets, outfile, indent=3)


def get_wordnet_pos(tag):
    if tag[1].startswith('J'):
        return wordnet.ADJ
    elif tag[1].startswith('S'):
        return wordnet.ADJ_SAT
    elif tag[1].startswith('V'):
        return wordnet.VERB
    elif tag[1].startswith('N'):
        return wordnet.NOUN
    elif tag[1].startswith('R'):
        return wordnet.ADV
    else:
        return ''

def cleaning_up(tweets):
    print("CLEANING...")
    clean =[]
    
    for tweet in tweets:
       
        tweet["text"] = html.unescape(html.unescape(tweet["text"]))
        tweet["text"] = re.sub(RE_TWEET, ERASE, tweet["text"]) 
        tweet["text"] = re.sub(HYPERLINKS, ERASE, tweet["text"]) #url
        tweet["text"] = re.sub(HASH, ERASE, tweet["text"]) #hash
        tweet["text"] = re.sub("@[^\s]+",ERASE,tweet["text"]) #tag username
        tweet["text"] =re.sub('<.*?>', ERASE, tweet["text"]) #tag html
        tweet["text"]= emoji.demojize(tweet["text"])
        tweet["text"] = re.sub(r":", ' ', tweet["text"])
        tweet["text"] = re.sub(r'\d+', '', tweet["text"]) #number
        tweet["text"] = tweet["text"].translate(str.maketrans('', '', string.punctuation))
    
        clean.append(tweet)
      
    print("---CLEANED---")

    return clean


def tweet_tokenize(tweets):
    
    print("TOKENIZATION...")
    all_tokens=[]
    tokens =[] 
    tokenizer = word_tokenize

    for tweet in tweets:
        temp=[]
        all_tokens = tokenizer(tweet["text"])
        lemmatizer = WordNetLemmatizer()
        stop_words = stopwords.words('english')
        for token in all_tokens:
                token = token.lower()
                if not (
                    not token.isalpha()
                    or token in stop_words 
                    or token in string.punctuation
                    or (token.isalpha() and len(token) < 2)):
                        tagged = nltk.pos_tag([token])
                        parsed = get_wordnet_pos(tagged[0])
                        if parsed != '':
                            token = lemmatizer.lemmatize(token, parsed)
                        temp.append(token)
        tokens.append(temp) 

    print("---TOKENIZED---")

    return tokens

def cleaned_users_tweets(tweets):
    print("CLEANING...")
    hashtags =[]
    for key in tweets:
    
        tweets[key] = html.unescape(html.unescape(tweets[key]))
        tweets[key] = re.sub(RE_TWEET, ERASE, tweets[key]) #re word
        tweets[key] = re.sub(HYPERLINKS, ERASE, tweets[key]) #url
        tweets[key] = re.sub(HASH, ERASE, tweets[key]) #hash
        tweets[key] = re.sub("@[^\s]+",ERASE,tweets[key]) #tag username
        tweets[key] = re.sub('<.*?>', ERASE, tweets[key]) #tag html
        tweets[key] = emoji.demojize(tweets[key])
        tweets[key]  = re.sub(r":", ' ', tweets[key])
        tweets[key] = re.sub(r'\d+', '', tweets[key]) #number
        tweets[key] = tweets[key].translate(str.maketrans('', '', string.punctuation))
     
    print("---DONE---") 
    return tweets


def user_tokenization(tweets):
    print("--USERS-TOKENIZATION...")
    all_tokens=[]
    tokens =[] 
    tokenizer = word_tokenize

    for key in tweets:
        temp=[]
        all_tokens = tokenizer(tweets[key])
        lemmatizer = WordNetLemmatizer()
        stop_words = stopwords.words('english')
        for token in all_tokens:
                token = token.lower()
                if not (
                    not token.isalpha()
                    or token in stop_words 
                    or (token.isalpha() and len(token) < 2)
                    or token in string.punctuation):
                        tagged = nltk.pos_tag([token])
                        parsed = get_wordnet_pos(tagged[0])
                        if parsed != '':
                            token = lemmatizer.lemmatize(token, parsed)
                        temp.append(token)

        tokens.append(temp)

    print("---TOKENIZED---")

    return tokens
  


nltk.download("stopwords")
nltk.download("punkt")
nltk.download("wordnet")
nltk.download('averaged_perceptron_tagger')
print("All extra packages installed successfully.")

topic_file = os.path.join("repository", "topic_tweets", "topics.json")
output_file = os.path.join("repository", "topic_tweets", "clean_topics.json")
pickle_file =  os.path.join("repository", "topic_tweets", "topics.pkl")
tweets = read_tweet(topic_file)
cleaned_tweets = cleaning_up(tweets)
with open(output_file, "w") as outfile:
        json.dump(cleaned_tweets, outfile, indent=3)

tweet_tokens = tweet_tokenize(cleaned_tweets)

with open(pickle_file, "wb") as writer:
    pickle.dump(tweet_tokens, writer)

for user in USER:
    path = os.path.join("repository", "users_tweets", user + ".json")
    pickle_user = os.path.join("repository", "users_tweets", user + ".pkl")
    user_tweets = read_tweet(path)
    cleaned_users = cleaned_users_tweets(user_tweets)
    save_user_tweets(user, cleaned_users)
    user_tokenize = user_tokenization(cleaned_users)
    with open(pickle_user, "wb") as writer:
        pickle.dump(user_tokenize, writer)


