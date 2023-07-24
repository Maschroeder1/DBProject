import os

with os.scandir('./scraper_trending') as entries:
    i = 0
    for entry in entries:
        j = 0
        with open(f'./scraper_trending/{entry.name}', 'r', encoding='utf-8') as f:
            for line in f:
                j += 1
            i += j
            print(f'File {entry.name} lines: {j}, Total: {i}')