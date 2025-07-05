# hijack.py
import os
import requests
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from bs4 import BeautifulSoup
from config import AFFILIATE_TAG

TARGET_URLS = [
    'https://petapixel.com/2021/06/01/best-sennheiser-microphones-for-video/',
]

def fetch_html(url, headers=None, proxies=None):
    resp = requests.get(url, headers=headers or {}, proxies=proxies or {})
    resp.raise_for_status()
    return resp.text

def update_affiliate_tag(url):
    """
    Replace or append the 'tag' query parameter with our AFFILIATE_TAG.
    """
    parsed = urlparse(url)
    # Preserve all existing query params, replacing 'tag'
    query_params = dict(parse_qsl(parsed.query))
    query_params['tag'] = AFFILIATE_TAG
    new_query = urlencode(query_params)
    return urlunparse(parsed._replace(query=new_query))

def rewrite_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.select('a[href*="amazon.com/dp/"]'):
        original = a['href']
        a['href'] = update_affiliate_tag(original)
    return str(soup)

def save_html(url, new_html, output_dir='hijacked'):
    os.makedirs(output_dir, exist_ok=True)
    filename = urlparse(url).netloc.replace('.', '_') + '.html'
    path = os.path.join(output_dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"Saved hijacked page: {path}")

def main():
    for url in TARGET_URLS:
        html = fetch_html(url)
        new_html = rewrite_links(html)
        save_html(url, new_html)

if __name__ == '__main__':
    main()
