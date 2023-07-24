import os
import urllib.parse
from bs4 import BeautifulSoup

dates = {}
with os.scandir('./scraper_htmls') as entries:
    i = 0
    for entry in entries:
        tree = ''
        date = entry.name[:10]
        if date not in dates:
            print(f'Adding {date} to dates. Current length: {len(dates)}')
            dates[date] = set()
        with open(f'./scraper_htmls/{entry.name}', 'rb') as file:
            tree = BeautifulSoup(file.read(), 'html.parser')
            trending = [a.text for a in tree.find(id='trends').find_all('a')][:-1]
            if len(trending) != 50:
                print(f'Unexpected amount of tags: {len(trending)} for {entry.name}')
            for elem in trending:
                dates[date].add(elem)
        i += 1
        # if i > 50:
        #     break

sorted_keys = sorted(dates.keys())
for i in range(len(sorted_keys)):
    current_date = sorted_keys[i]
    print(f'Saving results from {current_date}')
    next_date = sorted_keys[i+1] if i < len(sorted_keys) - 1 else '2023_05_01'
    with open(f'./scraper_trending/{current_date}', 'w', encoding='utf-8') as outfile:
        for elem in sorted(dates[current_date]):
            outfile.write(f'{elem}\n')
    with open(f'./scraper_urls/{current_date}', 'w', encoding='utf-8') as outfile:
        for elem in sorted(dates[current_date]):
            url = 'https://twitter.com/search?q='
            if elem[0] == '#':
                url += f'({urllib.parse.quote_plus(elem)})'
                # https://twitter.com/search?q=(%233X3U)     %20lang%3Aen%20until%3A2019-04-06%20since%3A2019-04-05&src=typed_query
            else:
                url += f'{urllib.parse.quote_plus(elem)}'
                # https://twitter.com/search?q=Chris%20Darden%20lang%3Aen%20until%3A2019-04-05%20since%3A2019-04-04&src=typed_query
            url += f'%20lang%3Aen%20until%3A{next_date.replace("_", "-")}%20since%3A{current_date.replace("_", "-")}&src=typed_query'
            outfile.write(f'{url}\n')

# for elem in trending:
#     print(elem)


