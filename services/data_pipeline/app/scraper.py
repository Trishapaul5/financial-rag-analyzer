"""
Financial News Scraper (Multi-Source Robust Version)
Scrapes articles from a variety of configured sources, with improved filtering and validation.
"""
import time
import logging
from typing import List, Dict, Set
from datetime import datetime
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from newspaper import Article
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Setup basic logging to provide clear feedback during the scraping process
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# A list of keywords used to validate if an article is financially relevant.
# This prevents non-financial news from polluting the database.
FINANCIAL_KEYWORDS = [
    'stock', 'market', 'nse', 'bse', 'sensex', 'nifty', 'ipo', 'fpo', 'equity',
    'shares', 'invest', 'trading', 'rbi', 'earnings', 'quarter', 'profit',
    'revenue', 'economy', 'gdp', 'inflation', 'gst', 'finance', 'brokerage', 'fed'
]

class FinancialNewsScraper:
    """A config-driven scraper with content validation for multiple financial news websites."""
    def __init__(self, config: Dict):
        self.config = config
        self.selenium_driver = None

    def _setup_selenium(self):
        """Initializes a headless Selenium WebDriver for sites that require JavaScript."""
        if self.selenium_driver is None:
            logger.info("Setting up Selenium WebDriver...")
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            self.selenium_driver = webdriver.Chrome(options=chrome_options)

    def _is_relevant(self, text: str, title: str) -> bool:
        """
        Validates if the article content is financially relevant based on keywords and length.
        This is a crucial step to ensure data quality.
        """
        if not text or len(text) < 300: # Filter out articles with very short content
            return False
        if "etprime member" in text.lower() or "subscribe to read" in text.lower(): # Filter paywalls
            return False
        
        combined_text = (title + ' ' + text).lower()
        # Check if at least two distinct financial keywords are present
        found_keywords = sum(1 for keyword in FINANCIAL_KEYWORDS if keyword in combined_text)
        return found_keywords >= 2

    def _extract_article_content(self, url: str) -> Dict:
        """
        Extracts structured content from a given article URL using the newspaper3k library
        and validates its relevance before returning the data.
        """
        try:
            article = Article(url)
            article.download()
            article.parse()

            if self._is_relevant(article.text, article.title):
                # If no publish date is found, default to the current time
                publish_date = article.publish_date.isoformat() if article.publish_date else datetime.now().isoformat()
                return {
                    'url': url,
                    'title': article.title,
                    'text': article.text,
                    'publish_date': publish_date,
                    'scraped_at': datetime.now().isoformat()
                }
            else:
                logger.warning(f"Skipping irrelevant or paywalled article: {url}")
                return None
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None

    def _scrape_source(self, source_name: str, source_config: Dict) -> List[Dict]:
        """Scrapes a single news source, filtering links intelligently."""
        logger.info(f"Scraping source: {source_name}...")
        articles = []
        base_url = source_config['base_url']
        
        for section in source_config['sections']:
            section_url = urljoin(base_url, section)
            try:
                if source_config.get('requires_selenium'):
                    self._setup_selenium()
                    self.selenium_driver.get(section_url)
                    time.sleep(3)
                    soup = BeautifulSoup(self.selenium_driver.page_source, 'html.parser')
                else:
                    response = requests.get(section_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                
                links = soup.select("a[href]")
                unique_urls: Set[str] = set()
                
                for link in links:
                    href = link['href']
                    # More robust regex to find article-like URLs from various sites
                    if re.search(r'/\d{6,}|/news/|/article/|/opinion/|/story/', href):
                        full_url = urljoin(base_url, href)
                        # Avoid section pages and other non-article links
                        if not any(x in full_url for x in ['/category/', '/author/', '/topic/']):
                             unique_urls.add(full_url)
                
                logger.info(f"Found {len(unique_urls)} potentially relevant links in section '{section}'.")

                for url in list(unique_urls)[:7]: # Limit to 7 articles per section to keep runs fast
                    article_data = self._extract_article_content(url)
                    if article_data:
                        article_data['source'] = source_name
                        article_data['section'] = section
                        articles.append(article_data)
                    time.sleep(1) # Be respectful to the server

            except Exception as e:
                logger.error(f"Failed to scrape section {section_url}: {e}")
        
        return articles

    def scrape_all(self) -> List[Dict]:
        """Scrapes all sources that are enabled in the configuration file."""
        all_articles = []
        for source_name, source_config in self.config['news_sources'].items():
            if source_config.get('scrape_enabled'):
                all_articles.extend(self._scrape_source(source_name, source_config))
        
        if self.selenium_driver:
            self.selenium_driver.quit()
            
        logger.info(f"Total RELEVANT articles scraped from all sources: {len(all_articles)}")
        return all_articles
