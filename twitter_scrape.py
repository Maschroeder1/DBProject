import os
import json
from bs4 import BeautifulSoup

def main():
    with os.scandir('./twitter_htmls') as entries:
        # entries = ['./test']
        # file_names = entries
        file_names = sorted([entry.name.split('.')[0] for entry in entries])
        total = 0
        for file_name in file_names:
            with open(f'./twitter_htmls/{file_name}.html', 'rb') as file:
            # with open(f'./{file_name}.html', 'rb') as file:
                with open(f'./twitter_tweets/{file_name}.json', 'w', encoding='utf-8') as outfile:
                # with open(f'./{file_name}.json', 'w', encoding='utf-8') as outfile:
                    print(f'Starting {file_name}')
                    tweets = get_tweets(BeautifulSoup(file.read().decode('utf-8'), 'html.parser'))
                    outfile.write(json.dumps(tweets, indent=4, ensure_ascii=False))
                    print(f'Writing {len(tweets)} to {file_name}')
                    total += len(tweets)
        print(f'Wrote total of {total} tweets')

def get_tweets(tree: BeautifulSoup):
    tweets = []
    with open('./temp.html', 'w', encoding='utf-8') as pain:
        for tweet_tree in tree.find_all(attrs={'data-testid':'tweet'}):
            # print('New tweet')
            tweet = {}
            tweet['user_name'] = get_user_name(tweet_tree, pain)
            tweet['user_id'] = get_user_id(tweet_tree, pain)
            tweet['text'] = get_text(tweet_tree, pain)
            tweet['id'] = get_id(tweet_tree, pain)
            tweet['engagement'] = get_engagement(tweet_tree, pain).split(', ')
            tweet['retweets'] = get_retweets(tweet['engagement'])
            tweet['replies'] = get_replies(tweet['engagement'])
            tweet['likes'] = get_likes(tweet['engagement'])
            tweet['sponsored'] = is_sponsored(tweet_tree, pain)
            tweets.append(tweet)
            # print(tweet)
    return tweets

def is_sponsored(tweet: BeautifulSoup, pain):
    return bool(tweet.find(class_='css-901oao r-14j79pv r-37j5jr r-n6v787 r-16dba41 r-1cwl3u0 r-bcqeeo r-qvutc0'))

def get_user_name(tweet: BeautifulSoup, pain):
    name_block = tweet.find(class_='css-901oao css-16my406 css-1hf3ou5 r-poiln3 r-bcqeeo r-qvutc0')
    if name_block == None:
        print('Unable to extract user name')
        return None
    user_name = ''.join([a.text for a in name_block.find_all(class_='css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0')])
    emojis = ''.join([img['alt'] for img in name_block.find_all('img', alt=True)])
    user_name += emojis
    if not len(user_name):
        print('Empty username')
        return None
    # pain.write(f'{user_name}\n')
    return user_name

def get_user_id(tweet: BeautifulSoup, pain):
    name_block = tweet.find(class_='css-901oao css-1hf3ou5 r-14j79pv r-18u37iz r-37j5jr r-1wvb978 r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-qvutc0')
    if name_block == None:
        print('Unable to extract user id')
        return None
    # pain.write(f'{str(name_block)}\n')
    return name_block.text

def get_text(tweet: BeautifulSoup, pain):
    texts = tweet.find(attrs={'data-testid':'tweetText'})
    if texts == None:
        print('Unable to extract tweet text')
        return None
    text = ''.join([text.text for text in texts])
    # pain.write(f'{text}\n')
    return text

def get_id(tweet: BeautifulSoup, pain):
    tweet_id = tweet.find(class_='css-4rbku5 css-18t94o4 css-901oao r-14j79pv r-1loqt21 r-xoduu5 r-1q142lx r-1w6e6rj r-37j5jr r-a023e6 r-16dba41 r-9aw3ui r-rjixqe r-bcqeeo r-3s2u2q r-qvutc0')
    if tweet_id == None:
        print('Unable to extract tweet id')
        return None
    # pain.write(f'{str(tweet_id)}\n')
    return 'https://twitter.com' + str(tweet_id['href']) if tweet_id else None

def get_engagement(tweet: BeautifulSoup, pain):
    engagement = tweet.find(class_='css-1dbjc4n r-1kbdv8c r-18u37iz r-1wtj0ep r-1s2bzr4 r-hzcoqn')
    if engagement == None:
        print('Unable to extract engagement metrics')
        return ''
    # pain.write(f'{str(engagement)}\n')
    engagement = engagement['aria-label']
    if engagement == None:
        print('Empty engagement metrics')
        return ''
    # print(engagement)
    return engagement

def get_retweets(engagement):
    retweets = [s for s in engagement if 'repo' in s.lower() or 'retw' in s.lower()]
    if len(retweets) != 1:
        print(f'Expected 1 got {len(retweets)} retweet count')
        return 0 if len(retweets) == 0 else -1
    else:
        return int(retweets[0].split()[0])

def get_replies(engagement):
    replies = [s for s in engagement if 'repl' in s.lower() or 'resposta' in s.lower()]
    if len(replies) != 1:
        print(f'Expected 1 got {len(replies)} reply count')
        return 0 if len(replies) == 0 else -1
    else:
        return int(replies[0].split()[0])

def get_likes(engagement):
    likes = [s for s in engagement if 'like' in s.lower() or 'curtida' in s.lower()]
    if len(likes) != 1:
        print(f'Expected 1 got {len(likes)} reply count')
        return 0 if len(likes) == 0 else -1
    else:
        return int(likes[0].split()[0])

if __name__ == '__main__':
    main()