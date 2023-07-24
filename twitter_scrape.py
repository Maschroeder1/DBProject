import os
import json
from bs4 import BeautifulSoup

def main():
    with os.scandir('./twitter_htmls') as entries:
        file_names = sorted([entry.name.split('.')[0] for entry in entries])
        for file_name in file_names:
            with open(f'./twitter_htmls/{file_name}.html', 'rb') as file:
                with open(f'./twitter_tweets/{file_name}.json', 'w', encoding='utf-8') as outfile:
                    tweets = get_tweets(BeautifulSoup(file.read().decode('utf-8'), 'html.parser'))
                    outfile.write(json.dumps(tweets, indent=4, ensure_ascii=False))
                    print(f'Writing {len(tweets)} to {file_name}')

def get_tweets(tree: BeautifulSoup):
    tweets = []
    with open('./temp.html', 'w', encoding='utf-8') as pain:
        for tweet_tree in tree.find_all(attrs={'data-testid':'tweet'}):
            if not is_sponsored(tweet_tree, pain):
                # print('New tweet')
                tweet = {}
                tweet['user_name'] = get_user_name(tweet_tree, pain)
                tweet['user_id'] = get_user_id(tweet_tree, pain)
                tweet['text'] = get_text(tweet_tree, pain)
                tweet['id'] = get_id(tweet_tree, pain)
                tweet['photo'] = get_photo(tweet_tree, pain)
                tweets.append(tweet)
                # print(tweet)
    return tweets

def is_sponsored(tweet: BeautifulSoup, pain):
    return tweet.find(class_='css-901oao r-14j79pv r-37j5jr r-n6v787 r-16dba41 r-1cwl3u0 r-bcqeeo r-qvutc0')

def get_user_name(tweet: BeautifulSoup, pain):
    name_block = tweet.find(class_='css-901oao css-16my406 css-1hf3ou5 r-poiln3 r-bcqeeo r-qvutc0')
    user_name = ''.join([a.text for a in name_block.find_all(class_='css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0')])
    emojis = ''.join([img['alt'] for img in name_block.find_all('img', alt=True)])
    user_name += emojis
    # pain.write(f'{user_name}\n')
    return user_name

def get_user_id(tweet: BeautifulSoup, pain):
    name_block = tweet.find(class_='css-901oao css-1hf3ou5 r-14j79pv r-18u37iz r-37j5jr r-1wvb978 r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-qvutc0')
    # pain.write(f'{str(name_block)}\n')
    return name_block.text

def get_text(tweet: BeautifulSoup, pain):
    texts = tweet.find(attrs={'data-testid':'tweetText'})
    text = ''.join([text.text for text in texts])
    # pain.write(f'{text}\n')
    return text

def get_id(tweet: BeautifulSoup, pain):
    tweet_id = tweet.find(class_='css-4rbku5 css-18t94o4 css-901oao r-14j79pv r-1loqt21 r-xoduu5 r-1q142lx r-1w6e6rj r-37j5jr r-a023e6 r-16dba41 r-9aw3ui r-rjixqe r-bcqeeo r-3s2u2q r-qvutc0')
    pain.write(f'{str(tweet_id)}\n')
    return 'https://twitter.com' + str(tweet_id['href']) if tweet_id else None

def get_photo(tweet: BeautifulSoup, pain):
    tweet_photo = tweet.find(attrs={'data-testid':'tweetPhoto'})
    pain.write(f'{str(tweet_photo)}\n')

if __name__ == '__main__':
    main()