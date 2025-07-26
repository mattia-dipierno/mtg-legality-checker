import requests
from bs4 import BeautifulSoup
import re

def estrai_mazzo(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }

    try:
        response = requests.Session()
        response.headers.update(headers)
        page = response.get(url, timeout=10)
        if page.status_code != 200:
            return {}, {}
    except:
        return {}, {}

    soup = BeautifulSoup(page.content, 'html.parser')
    deck_input = soup.find('input', {'id': 'deck_input_deck'})

    if not deck_input:
        return {}, {}

    raw_lines = deck_input.get('value', '').strip().split('\n')

    main_deck = {}
    sideboard = {}

    current_section = main_deck
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
        if line.lower() == 'sideboard':
            current_section = sideboard
            continue
        match = re.match(r'^(\d+)\s+(.+)$', line)
        if match:
            qty = int(match.group(1))
            name = match.group(2).strip()
            current_section[name] = current_section.get(name, 0) + qty

    return main_deck, sideboard

