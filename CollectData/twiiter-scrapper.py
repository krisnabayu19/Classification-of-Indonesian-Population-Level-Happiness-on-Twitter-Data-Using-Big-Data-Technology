import json
import snscrape.modules.twitter as sntwitter
import tweepy
from pymongo import MongoClient
from tweepy import OAuthHandler

client = MongoClient('localhost', 27017)
db = client['nama_database']
collection = db['nama_collection']

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

last_id: int = 128681341227028889617281737

while True :
    try :
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper('since:2020-08-20 until:2020-08-21 + lang:in').get_items()):

            id = tweet.id
            print("id = ", id)
            print("last id", last_id)
            if last_id <= id:
                print("sudah diambil")
                continue
            else :
                last_id = id
                getTweet = api.get_status(id, wait_on_rate_limit=True, tweet_mode='extended')
                json_str = json.dumps(getTweet._json)
                print(json_str)
                collection.insert_one(getTweet._json)
                continue

    except:
        print("Data tidak masuk")