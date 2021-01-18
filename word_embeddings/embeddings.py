import gensim
from gensim.models.word2vec import Word2Vec
import os
import json
import pickle
from gensim.models.phrases import Phrases, Phraser
from setup.config import USER
from collections import Counter

def read_tweet(filepath):   
    with open(filepath, 'rb') as handle:
       data = pickle.load(handle)
    return data 

def get_word_frequencies(corpus):
  frequencies = Counter()
  for sentence in corpus:
    for word in sentence:
      frequencies[word] += 1
  freq = frequencies.most_common()
  return freq

  
topics_pickle = os.path.join("repository", "topic_tweets", "topics.pkl")
topics_tweet = read_tweet(topics_pickle)
topics_model = Word2Vec(topics_tweet, sg=0,
                            seed = 1,
                            sample=0,
                            window=5,
                            min_count= 2 )

topics_model.save('models/topics.model')

for user in USER:
   
    user_tokens = os.path.join("repository", "users_tweets", user + ".pkl")
    user_tweet = read_tweet(user_tokens)

    user_model = Word2Vec(user_tweet, sg=0,
                            seed = 1,
                            sample=0,
                            window=5,
                            min_count= 2)
    user_model.save('models/'+user+'.model')