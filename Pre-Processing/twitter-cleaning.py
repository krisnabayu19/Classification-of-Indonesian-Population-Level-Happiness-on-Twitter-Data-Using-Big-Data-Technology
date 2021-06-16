from pymongo import MongoClient
import pymongo
import pandas as pd
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import re
import string
import json
import csv
import functools
import operator
import re
import emoji
import string

# Connection to MongoDB
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["nama_database_save"]
mycol = mydb["nama_collection_save"]

# Stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# array stopword list
stopwords = []

# array stop words list text input
stopwords_list = []


def _connect_mongo(host, port, username, password, db):
    """ A util for making a connection to mongo """

    if username and password:
        mongo_uri = 'mongodb://localhost:27017/' % (username, password, host, port, db)
        conn = MongoClient(mongo_uri)
    else:
        conn = MongoClient(host, port)
    return conn[db]


def read_mongo(db, collection, query={}, host='localhost', port=27017, username=None, password=None, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Connect to MongoDB
    db = _connect_mongo(host=host, port=port, username=username, password=password, db=db)

    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)

    # Expand the cursor and construct the DataFrame
    df =  pd.DataFrame(list(cursor))

    # Delete the _id
    if no_id and '_id' in df:
        del df['_id']

    return df

# Function to Clean
def clean_tweet(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|(_[A-Za-z0-9]+)|(\w+:\/\/\S+)|(\d+)|"
                           "(\s([@#][\w_-]+)|(#\\S+))|((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))", " ", tweet).replace(",","").replace(".","").replace("?","").replace("!","").replace("/","").replace("&","").replace(":","").replace("_","").replace("@","").replace("#","").split())


if __name__ == '__main__':

    # get data from database MongoDB
    df = read_mongo('nama_database_get', 'nama_collection_get', {})

    # open stop words list
    with open('list_stopwords.csv', 'r') as file:
        for line in file:
            clear_line = line.replace("\n", '').strip()
            stopwords.append(clear_line)

    # Looping for get tweet to cleaning
    for index, row in df.iterrows():

        text = row['text']
        final_words = []
        after_stopwords = []

        # cleaning process
        gas = text.strip()
        blob = clean_tweet(gas)
        print("Text Cleaning :",blob)
        
        # split text and emoticon
        em_split_emoji = emoji.get_emoji_regexp().split(blob)
        em_split_whitespace = [substr.split() for substr in em_split_emoji]
        em_split = functools.reduce(operator.concat, em_split_whitespace)
        strSplit = ' '.join(em_split)
        print("Text Split Emoticon and Text :", strSplit)

        # lowering case process
        lower_case = strSplit.lower()
        print("Text Lower Case :",lower_case)
        
        # convert emoticon process
        punctuationText = lower_case.translate(str.maketrans('', '', string.punctuation))
        tokenized_words = punctuationText.split()
        for tokenized_words_emoticon in tokenized_words:
            arrayTokenizingEmoticon = []
            arrayTokenizingEmoticon.append(tokenized_words_emoticon)

            with open('list_emoji_emosi_bahagia_tidakbahagia.csv', 'r',encoding='utf-8') as fileEmoticon:
                for lineEmoticon in fileEmoticon:
                    clear_line_emoticon = lineEmoticon.replace("\n", '').strip()
                    emoticon, convert = clear_line_emoticon.split(',')
                    if emoticon in arrayTokenizingEmoticon:
                        tokenized_words.append(convert)
        strEmoticonConvert = ' '.join(tokenized_words)
        print("Text Emoticon Convert :",strEmoticonConvert)

        # stemming process
        hasilStemmer = stemmer.stem(strEmoticonConvert)
        print("Text Stemming :",hasilStemmer)

        # stop words process
        punctuationText2 = hasilStemmer.translate(str.maketrans('', '', string.punctuation))
        tokenized_words2 = punctuationText2.split()
        for tokenized_words3 in tokenized_words2:
            if tokenized_words3 not in stopwords:
                stopwords_list.append(stopwords)
                after_stopwords.append(tokenized_words3)

        strTextFix = ' '.join(after_stopwords)
        

        # Variable After Cleanning Tweets
        mongo = {
            "id": row["id"],
            "created_at": row["created_at"],
            "text": strTextFix,
            "place_object":row["place_object"],
            "language": row["language"]
        }

        # Print Variable MongoDB
        print(mongo)

        # Save to MongoDB
        x = mycol.insert_one(mongo)