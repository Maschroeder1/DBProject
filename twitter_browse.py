from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import re
import time
import json

# ultimo 2019: 2019_04_05_Pominville.html
first_failed = '2021_01_02_TufBorland.html'
dry_run = False
wait_between_times = [10, 300, 10]
cookies_file = './cookies2.json'

driver = None
found_success = False
start_time = ''
entry_time = ''

def main():
    with os.scandir('./scraper_urls') as entries:
        global start_time
        global entry_time
        global driver
        sorted_entries = sorted([entry.name for entry in entries])
        if not dry_run:
            driver = get_driver()
        start_time = time.time()
        for entry in sorted_entries:
            entry_time = time.time()
            print(f'Starting {entry}')
            with open(f'./scraper_urls/{entry}', 'r') as f:
                for twitter_url in f:
                    got_html = False
                    attempt = 0
                    while not got_html and attempt < len(wait_between_times):
                        got_html = get_html(entry, twitter_url, wait_between_times[attempt])
                        attempt += 1
                    if not got_html:
                        print('Error, finishing')
                        return
    if not dry_run:
        driver.close()

def get_html(entry: str, twitter_url: str, sleep_time: int):
    global found_success
    file_name = get_file_name(entry, twitter_url)
    if file_name == first_failed:
        print(f'Found {first_failed}, will start from next line')
        time.sleep(3)
        found_success = True
    if found_success:
        if not dry_run:
            driver.get(twitter_url)
            html = poll_html(sleep_time, file_name, twitter_url)
            with open(f'./twitter_htmls/{file_name}', 'w', encoding='utf-8') as outfile:
                print(f'Writing {file_name} {entry} time: {int(time.time() - entry_time)}, total time: {int(time.time() - start_time)}')
                outfile.write(html)
            if not is_success(html, file_name, twitter_url):
                return False
        else:
            print(file_name)
            time.sleep(1)
    return True

def poll_html(sleep_time: int, file_name: str, url: str):
    html = ''
    for _ in range(sleep_time):
        time.sleep(1)
        html = driver.page_source
        if is_success(html, file_name, url):
            return html
    return html

def is_success(html: str, file_name: str, url: str):
    if 'Sorry, you are rate limited. Please wait a few moments then try again.' in html:
        print(f'Error {file_name} got rate-limited')
        return False
    if 'Something went wrong. Try reloading.' in html:
        print(f'Error {file_name} couldnt access {url}')
        return False
    if 'data-testid="tweet"' not in html:
        print(f'Error {file_name} couldnt get tweets {url}')
        return False
    return True
    

def get_file_name(entry: str, twitter_url: str):
    file_name = twitter_url[29:twitter_url.find('%20lang')]
    is_hashtag = file_name.startswith('(%23')
    if is_hashtag:
        file_name = file_name[4:-1]
    file_name = re.sub(r'[\W_]', '', file_name)
    prefix = f'{entry}_hashtag' if is_hashtag else entry
    
    return f'{prefix}_{file_name}.html'

def get_driver():
    opts = Options()
    # opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246')
    driver = webdriver.Chrome(opts)
    driver.get("https://twitter.com/Sarah_Stierch/status/1682956793218240514")
    cookies = {}
    with open(cookies_file, 'r') as f:
        cookies = json.load(f)
    for cookie in cookies:
        driver.add_cookie(cookie)

    return driver

if __name__ == '__main__':
    main()