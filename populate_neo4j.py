import json
import os
import re
import time
from neo4j import GraphDatabase

small = True
tweets_folder = './twitter_tweets'
session = GraphDatabase.driver(uri='bolt://localhost:7687', auth=('neo4j', 'abcd1234')).session()
excluded_words = set()
excluded_words.add('http')
excluded_words.add('https')

def main():
    with os.scandir(tweets_folder) as entries:
        file_names = sorted([entry.name.split('.')[0] for entry in entries])
        filter_small = ''
        total_tweets = 0
        start_time = time.time()
        for file_name in file_names:
            consume_file = not small or filter_small != file_name[:7]
            filter_small = file_name[:7]
            tweets = []
            if consume_file:
                print(f'Consuming {file_name}')
                tweets = read_file(file_name)
                for tweet in tweets:
                    insert(sanitize(tweet), file_name[:10])
                total_tweets += len(tweets)
                print(f'{file_name} Tweet count: {len(tweets)}. Total: {total_tweets} in {int(time.time() - start_time)}sec\n')

def read_file(file_name: str):
    with open(f'./twitter_tweets/{file_name}.json', 'r', encoding='utf8') as f:
        return json.load(f)

def sanitize(tweet: dict):
    for key in tweet.keys():
        if type(tweet[key]) == type(''):
            tweet[key] = re.sub(' +', ' ', tweet[key].replace('\n', ' ').replace('\r', ' ').replace('\\', '\\\\').replace('"', "'"))
            # print(tweet[key])
    return tweet

def insert(tweet: dict, date: str):
    [year, month, day] = date.split('_')
    date_statement = f'date:DATE {{name:"{date}", year:{int(year)}, month:{int(month)}, day:{int(day)}}}'
    user_statement = f'twitter_user:TWITTER_USER {{name:"{tweet["user_name"]}", id:"{tweet["user_id"]}"}}'
    tweet_statement = f'tweet:TWEET {{id:"{tweet["id"]}", text:"{tweet["text"]}", likes:{tweet["likes"]}, retweets:{tweet["retweets"]}, replies:{tweet["replies"]}, sponsored:{tweet["sponsored"]}}}'
    # likes_statement = f'like:LIKE {{count:"{tweet["likes"]}"}}'
    # retweets_statement = f'retweet:RETWEET {{count:"{tweet["retweets"]}"}}'
    # replies_statement = f'reply:REPLY {{count:"{tweet["replies"]}"}}'

    words = tokenize(tweet['text'])
    session.run(f'MERGE ({date_statement})')
    session.run(f'MERGE ({user_statement})')
    session.run(f'MERGE ({tweet_statement})')
    # session.run(f'MERGE ({likes_statement})')
    # session.run(f'MERGE ({retweets_statement})')
    # session.run(f'MERGE ({replies_statement})')
    
    session.run(f'MATCH ({user_statement}), ({tweet_statement})\nMERGE (twitter_user)-[:TWEETED]->(tweet)')
    session.run(f'MATCH ({tweet_statement}), ({date_statement})\nMERGE (tweet)-[:CREATED_AT]->(date)')
    # session.run(f'MATCH ({tweet_statement}), ({likes_statement})\nMERGE (tweet)-[:LIKED]->(like)')
    # session.run(f'MATCH ({tweet_statement}), ({retweets_statement})\nMERGE (tweet)-[:RETWEETED]->(retweet)')
    # session.run(f'MATCH ({tweet_statement}), ({replies_statement})\nMERGE (tweet)-[:REPLIED]->(reply)')

    for word in words:
        word_statement = f'word:WORD {{value:"{word}"}}'
        session.run(f'MERGE ({word_statement})')
        session.run(f'MATCH ({tweet_statement}), ({word_statement})\nMERGE (tweet)-[:CONTAINS]->(word)')
    # raise Exception

def tokenize(text: str):
    new_text = re.sub('[^a-z0-9@#.,%]', ' ', text.lower())
    new_text = re.sub('(,|\.)[a-z ]', ' ', new_text)
    new_text = re.sub('[a-z ](,|\.)', ' ', new_text)
    return [a for a in new_text.split() if len(a) > 1 and a not in excluded_words]

if __name__ == '__main__':
    main()