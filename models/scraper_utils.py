import requests
from bs4 import BeautifulSoup
import logging
import random

_logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
]

def parse_amazon(soup):
    # Try different Amazon price selectors
    price_element = soup.find('span', {'class': 'a-price-whole'})
    if not price_element:
        price_element = soup.find('span', {'class': 'a-color-price'})
    if price_element:
        # Simplistic extraction
        text = price_element.text.replace(',', '.').replace('$', '').replace('€', '').strip()
        try:
            return float(text)
        except ValueError:
            pass
    return None

def parse_google_shopping(soup):
    # Google Shopping typical price selector (subject to change)
    price_element = soup.find('span', {'class': 'g9WBQb'})
    if price_element:
        text = price_element.text.replace(',', '.').replace('$', '').replace('€', '').strip()
        try:
            return float(text)
        except ValueError:
            pass
    return None

def scrape_price(url, platform, proxy=None, api_provider=None, api_key=None, render_js=False, debug_mock=False):
    """
    Scrapes competitor prices.
    Uses randomized user-agents to bypass basic blocking.
    Allows passing a proxy string (e.g. "http://user:pass@proxy_ip:port") to route requests.
    Supports native integration with ScrapingBee or ZenRows.
    """
    _logger.info(f"Scraping {platform} URL: {url}")
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    
    proxies = None
    if proxy:
        proxies = {
            "http": proxy,
            "https": proxy
        }
        
    try:
        request_url = url
        params = {}
        
        # Native API Integrations
        if api_provider == 'scrapingbee' and api_key:
            request_url = "https://app.scrapingbee.com/api/v1/"
            params = {
                "api_key": api_key,
                "url": url,
                "render_js": "True" if render_js else "False"
            }
            # Remove custom headers for ScrapingBee as they manage it
            headers = {}
            proxies = None
        elif api_provider == 'zenrows' and api_key:
            request_url = "https://api.zenrows.com/v1/"
            params = {
                "apikey": api_key,
                "url": url,
                "js_render": "true" if render_js else "false"
            }
            headers = {}
            proxies = None

        response = requests.get(request_url, params=params, headers=headers, proxies=proxies, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        price = None
        if platform == 'amazon':
            price = parse_amazon(soup)
        elif platform == 'google':
            price = parse_google_shopping(soup)
        
        # If parsing fails or custom platform, return a mock price for development/testing if enabled
        if price is None:
            if debug_mock:
                _logger.warning(f"Could not parse price from {platform}, returning mock value for testing.")
                return round(random.uniform(10.0, 100.0), 2)
            _logger.warning(f"Could not parse price from {platform}. Returning None.")
            return None
            
        return price
    except Exception as e:
        _logger.error(f"Error scraping {url}: {e}")
        return None
