import os

source_urls_path = './scraper_urls'
target_urls_path = './scraper_urls_shallow'
source_urls = set()
target_urls = set()

def main():
    source_urls = get_urls(source_urls_path, get_entries(source_urls_path))
    target_urls = get_urls(target_urls_path, get_entries(target_urls_path))

    check_contains(source_urls_path, source_urls, target_urls)
    check_contains(target_urls_path, target_urls, source_urls)

def get_entries(path: str):
    with os.scandir(path) as entries:
        return sorted([entry.name for entry in entries if not (entry.name.startswith('2019') or entry.name.startswith('2020'))])

def get_urls(path: str, entries: list):
    urls = set()
    for entry in entries:
        with open(f'{path}/{entry}', 'r') as f:
            for line in f:
                urls.add(line.split(' - ')[1].strip())
    return urls

def check_contains(name: str, source: set, target: set):
    for url in source:
        if url not in target:
            print(f'{url} in {name} but not in other')

if __name__ == '__main__':
    main()