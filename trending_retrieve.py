import requests
import time

base_url = 'https://getdaytrends.com/united-states'
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'cache-control': 'no-cache'}
start_time = time.time()
last_time = time.time()

for year in range(2023,2024):
    for month in range(4, 5):
        for day in range(22, 32):
            for hour in range(0, 24):
                file_name = f'{year}_{month:02d}_{day:02d}_{hour:02d}'
                url = f'{base_url}/{year}-{month:02d}-{day:02d}/{hour}/'
                response = requests.request("GET", url, headers=headers, data={})
                loop_time = time.time()
                if response.status_code >= 200 and response.status_code < 300:
                    print(f'Success {file_name}. Loop time: {(loop_time - last_time):.2f}, total time: {int(loop_time - start_time)}')
                    with open(f'./scraper_htmls/{file_name}.html', 'w', encoding='utf-8') as outfile:
                        outfile.write(response.text)
                else:
                    print(f'Failure {file_name} {response.status_code}')
                last_time = loop_time
                # raise Exception