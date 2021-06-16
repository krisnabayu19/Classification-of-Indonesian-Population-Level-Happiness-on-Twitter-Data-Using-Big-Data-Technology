import tweepy
import json
import pymongo
from pymongo import MongoClient


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["nama_database"]
mycol = mydb["nama_collection"]

access_token = ""
access_token_secret = ""
api_key = ""
api_secret_key = ""

authentication = tweepy.OAuthHandler(api_key, api_secret_key)
authentication.set_access_token(access_token, access_token_secret)
api = tweepy.API(authentication)

places = api.geo_search(query="Indonesia", granularity="country")
last_id: int = 128681341227028889617281737

while True :
    try:
        for place in places:
            print("placeid:%s" % place)
            public_tweets = tweepy.Cursor(api.search, count=100, q="place:%s" % place.id ,
                                          show_user=True, tweet_mode="extended").items()
            for tweet in public_tweets:
                id = tweet.id
                print("id = ", id)
                print("last id", last_id)

                if last_id <= id:
                    print("sudah diambil")
                    continue
                else:
                    last_id = tweet.id
                    json_str = json.dumps(tweet._json)
                    print(json_str)
                    mycol.insert_one(tweet._json)
                    continue
    except:
        print("Data Tidak Masuk")