# hijack.py
import os
import requests
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from bs4 import BeautifulSoup
from config import AFFILIATE_TAG

# Realistic browser User-Agent to avoid simple bot blocks
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
}

# Updated, live PetaPixel article URL
TARGET_URLS = [
    'https://petapixel.com/2025/05/14/sennheisers-199-one-mic-profile-wireless-system-is-for-solo-creators/',
]

def fetch_html(url, headers=None, proxies=None):
    resp = requests.get(url, headers=headers or HEADERS, proxies=proxies or {})
    resp.raise_for_status()
    return resp.text

def update_affiliate_tag(url):
    """
    Replace or append the 'tag' query parameter with our AFFILIATE_TAG.
    """
    parsed = urlparse(url)
    params = dict(parse_qsl(parsed.query))
    params['tag'] = AFFILIATE_TAG
    new_query = urlencode(params)
    return urlunparse(parsed._replace(query=new_query))

def rewrite_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.select('a[href*="amazon.com/dp/"]'):
        a['href'] = update_affiliate_tag(a['href'])
    return str(soup)

def save_html(url, new_html, output_dir='hijacked'):
    os.makedirs(output_dir, exist_ok=True)
    name = urlparse(url).path.strip('/').replace('/', '_') or 'index'
    filename = f"{urlparse(url).netloc.replace('.', '_')}_{name}.html"
    path = os.path.join(output_dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"✅ Saved hijacked page: {path}")

def main():
    for url in TARGET_URLS:
        try:
            print(f"→ Fetching: {url}")
            html = fetch_html(url)
        except requests.HTTPError as e:
            print(f"⚠️  Failed to fetch {url}: {e}")
            continue

        new_html = rewrite_links(html)
        save_html(url, new_html)

if __name__ == '__main__':
    main()