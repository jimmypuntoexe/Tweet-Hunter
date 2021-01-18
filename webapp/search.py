import os
import json
import itertools
import numpy as np
from elasticsearch import Elasticsearch
from gensim.models.word2vec import Word2Vec
from gensim.models.phrases import Phraser
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize.casual import TweetTokenizer
import string
import html
import re
import emoji

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


query_embeddings = Word2Vec.load(os.path.join("models", "topics.model"))
user_embeddings = {}
def cleaning_up(query):
    print("CLEANING...", query)

    query = html.unescape(html.unescape(query))
    query = re.sub(RE_TWEET, ERASE, query) 
    query = re.sub(HYPERLINKS, ERASE, query) #url
    query = re.sub(HASH, ERASE, query) #hash
    query = re.sub("@[^\s]+",ERASE,query) #tag username
    query =re.sub('<.*?>', ERASE, query) #tag html
    query = emoji.demojize(query)
    query = re.sub(r":", ' ', query)
       
    query = re.sub(r'\d+', '', query) #number
        #tweet = re.sub(r'\s+', '', tweet) #whitespace
    query = query.translate(str.maketrans('', '', string.punctuation))
        #tweet = convert_emojis(tweet)
       
    
    print("---CLEANED---")

    return query


def tweet_tokenize(query):
    print("TOKENIZATION...")
    all_tokens=[]
    tokens =[] #right tokens
    tokenizer = word_tokenize
    
    #tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True,reduce_len=True)
    print(query)
    temp=[]
    all_tokens = tokenizer(query)
    lemmatizer = WordNetLemmatizer()
    stop_words = stopwords.words('english')
    for token in all_tokens:
                token = token.lower()
                token = lemmatizer.lemmatize(token)
                if not (
                    not token.isalpha()
                    or token in stop_words 
                    or token in string.punctuation):
                       tokens.append(token)

    print("---TOKENIZED---")

    return tokens
def search_query(query, user, topic, count, field):
    es = Elasticsearch()

    user_profile = False
    should = []
    must = []
    str_profile = []

    

    if field == "username":
        must.append({"query_string": {"query": query, "default_field": "user_name"}})
    elif field == "text":    
        must.append({"query_string": {"query": query, "default_field": "text"}})
    elif field == "hashtag":    
        must.append({"query_string": {"query": query, "default_field": "hashtags"}})

    if user != "None":
        user_embedding = None
        user_profile = True
        try:
            user_embedding = user_embeddings[user]
        except KeyError:
            user_embeddings[user] = Word2Vec.load(
            os.path.join("models", "@" + user + ".model"))
            user_embedding = user_embeddings[user]
        cleaned_query = cleaning_up(query)
        preprocessed_query = tweet_tokenize(cleaned_query)
        vectors = []
        shoulds = []
        for token in preprocessed_query:
            print("TOKEN ", token)
            try:
                vec = query_embeddings.wv.get_vector(token)
                vectors.append(vec)
            except KeyError:
                print("Token " + token + " not found in query embeddings")
        if vectors != []:
            for vector in vectors:
                shoulds.extend(
                    [
                        (word, sim)
                        for word, sim in user_embedding.wv.most_similar(
                            [vector], topn=10
                        )
                    ]
                )
            shoulds = sorted(shoulds, key=lambda x: x[1], reverse=True)
            shoulds = [word for word, sim in shoulds]
            shoulds = list(dict.fromkeys(shoulds).keys())[:10]
            shoulds = [word.split("_") for word in shoulds]
            shoulds = list(itertools.chain(*shoulds))
        should.append({"match": {"text": " ".join(shoulds)}})
        user_profile = True

 
    if topic != "None":
        must.append({"term": {"topic": topic}})

    print("SHOULD", should)

    q = {"must": must, "should": should}
    body = {
        "size": count,
        "query": {
            "function_score": {
                "query": {"bool": q},
                "functions": [
                    {
                        "exp": {
                            "created_at": {
                                "origin": "now",
                                "scale": "10d",
                                "offset": "5d",
                                "decay": 0.6,
                            }
                        }
                    },
                    {
                        "field_value_factor": {
                            "field": "like",
                            "factor": 1,
                            "modifier": "sqrt",
                            "missing": 1,
                        }
                    },
                    {
                        "field_value_factor": {
                            "field": "retweet",
                            "factor": 1,
                            "modifier": "sqrt",
                            "missing": 1,
                        }
                    },
                ],
                "score_mode": "multiply",
            }
        },
    }
    res = es.search(index="twindex", body=body)
    print("RES: \n", res)
    print("QUERY: \n", q)
    res = res["hits"]["hits"]
    if user_profile:
        return res, should[0]["match"]["text"]
    else:
        return res, " "