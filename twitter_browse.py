from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import os
import re
import time
import pickle

def main():
    driver = None
    first_failed = '2019_04_05_JustCause4.html'
    dry_run = False
    found_success = False
    with os.scandir('./scraper_urls') as entries:
        sorted_entries = sorted([entry.name for entry in entries])
        if not dry_run:
            driver = get_driver()
        start_time = time.time()
        for entry in sorted_entries:
            entry_time = time.time()
            print(f'Starting {entry}')
            with open(f'./scraper_urls/{entry}', 'r') as f:
                for twitter_url in f:
                    file_name = get_file_name(entry, twitter_url)
                    if file_name == first_failed:
                        print(f'Found {first_failed}, will start from next line')
                        time.sleep(3)
                        found_success = True
                    if found_success:
                        if not dry_run:
                            driver.get(twitter_url)
                            time.sleep(10)
                            html = driver.page_source
                            if not is_success(html, file_name, twitter_url):
                                return file_name
                            with open(f'./twitter_htmls/{file_name}', 'w', encoding='utf-8') as outfile:
                                print(f'Writing {file_name} {entry} time: {int(time.time() - entry_time)}, total time: {int(time.time() - start_time)}')
                                outfile.write(html)
                        else:
                            print(file_name)
                            time.sleep(1)
    if not dry_run:
        driver.close()

def is_success(html: str, file_name: str, url: str):
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
    driver.add_cookie({'name': 'personalization_id', 'value': ''})
    driver.add_cookie({'name': '_gcl_au', 'value': ''})
    driver.add_cookie({'name': '_ga', 'value': ''})
    driver.add_cookie({'name': '_gid', 'value': ''})
    driver.add_cookie({'name': '_ga_34PHSZMC42', 'value': ''})
    driver.add_cookie({'name': '_ga_ZJQNEMXF73', 'value': ''})
    driver.add_cookie({'name': '_ga_BYKEBDM7DS', 'value': ''})
    driver.add_cookie({'name': 'kdt', 'value': ''})
    driver.add_cookie({'name': 'mbox', 'value': ''})
    driver.add_cookie({'name': 'des_opt_in', 'value': ''})
    driver.add_cookie({'name': 'lang', 'value': ''})
    driver.add_cookie({'name': 'auth_token', 'value': ''})
    driver.add_cookie({'name': 'ct0', 'value': ''})
    driver.add_cookie({'name': 'twid', 'value': ''})
    driver.add_cookie({'name': 'guest_id_ads', 'value': ''})
    driver.add_cookie({'name': 'guest_id', 'value': ''})
    driver.add_cookie({'name': 'guest_id_marketing', 'value': ''})

    return driver

if __name__ == '__main__':
    main()