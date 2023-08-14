import os
import random

random.seed(123)

source_urls_path = './scraper_urls'
target_urls_path = './scraper_urls_shallow'

sorted_entries = []
with os.scandir(source_urls_path) as entries:
    sorted_entries = sorted([entry.name for entry in entries if not (entry.name.startswith('2019') or entry.name.startswith('2020'))])


complete = {}
for file in sorted_entries:
    topics = []
    hashtags = []
    with open(f'{source_urls_path}/{file}', 'r') as f:
        for line in f:
            if line.startswith('https://twitter.com/search?q=(%23'):
                hashtags.append(line.strip())
            else:
                topics.append(line.strip())
    if len(topics) or len(hashtags):
        complete[file] = topics + hashtags
    
    # print(f'{file}: tags {len(hashtags)} topics {len(topics)}')

i = 0
while len(complete):
    print(f'{len(complete)} - {i:03d}')
    selected = []
    for date in sorted(complete.keys()):
        index = random.randint(0, len(complete[date]) - 1) if len(complete[date]) > 1 else 0
        # print(f'{date} - {len(complete[date])} - {index}')
        selected.append(f'{date} - {complete[date][index]}')
        del complete[date][index]
        if not len(complete[date]):
            del complete[date]
    with open(f'{target_urls_path}/{i:03d}.txt', 'w') as outfile:
        for elem in selected:
            outfile.write(f'{elem}\n')
    # if i > 10:
    #     raise Exception
    i += 1

print(i)