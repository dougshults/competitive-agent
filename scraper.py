"""
Competitive Scraper
This module handles scraping of competitor content from various sources.
"""

import os
import logging
import html
import time
import re
import asyncio
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from functools import lru_cache
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import aiohttp

logger = logging.getLogger(__name__)

class CompetitiveScraper:
    """Scraper for competitive analysis."""
    
    # PropTech keywords for content filtering
    PROPTECH_KEYWORDS = [
        # === PEOPLE & ROLES ===
        'renters', 'tenants', 'landlords', 'property managers', 'property management',
        'real estate agents', 'real estate brokers', 'realtors', 'leasing agents',
        'property owners', 'homeowners', 'buyers', 'sellers', 'investors',
        'developers', 'contractors', 'architects', 'property inspectors',
        'agent', 'agents', 'broker', 'brokers', 'brokerage', 'brokerages',
        # === JARGON & INDUSTRY TERMS ===
        'MLS', 'escrow', 'title insurance', 'closing costs', 'listing agent', 'buyer agent',
        'dual agency', 'commission', 'open house', 'walkthrough', 'staging', 'zoning', 'permit',
        'deed', 'foreclosure', 'short sale', 'flip', 'fixer-upper', 'turnkey', 'cap rate', 'NOI',
        'cash flow', '1031 exchange', 'syndication', 'crowdfunding', 'fractional ownership',
        'blockchain real estate', 'tokenization', 'smart contract',
        # === PROPERTY TYPES ===
        'real estate', 'property', 'properties', 'housing', 'homes', 'houses',
        'apartments', 'condos', 'condominiums', 'townhomes', 'single family',
        'multi family', 'commercial property', 'commercial real estate',
        'office buildings', 'office space', 'retail space', 'warehouses',
        'industrial property', 'land', 'lots', 'vacant land',
        # === FINANCIAL & TRANSACTIONS ===
        'property values', 'home values', 'property valuation', 'appraisal',
        'mortgage', 'mortgages', 'lending', 'loan', 'refinancing',
        'down payment', 'escrow', 'title',
        'rent', 'rental', 'lease', 'leasing', 'rent control',
        'property taxes', 'hoa fees', 'maintenance costs',
        'investment property', 'property investment', 'real estate investment',
        'reit', 'real estate funds', 'crowdfunding real estate',
        # === TECHNOLOGY & PLATFORMS ===
        'proptech', 'property technology', 'real estate tech', 'real estate technology',
        'real estate platform', 'rental platform', 'property platform',
        'real estate app', 'property app', 'rental app',
        'property management software', 'real estate software',
        'smart building', 'smart home', 'iot building', 'building automation',
        'property analytics', 'real estate data', 'property data',
        'virtual tours', 'digital property', 'online real estate',
        # === BUSINESS MODELS & SERVICES ===
        'facility management', 'building management',
        'real estate services', 'property services', 'leasing services',
        'co-living', 'co-working', 'flexible space', 'shared space',
        'short term rental', 'vacation rental', 'corporate housing',
        'build to rent', 'rent to own', 'lease to own',
        'property marketplace', 'real estate marketplace',
        # === CONSTRUCTION & DEVELOPMENT ===
        'construction', 'construction tech', 'building', 'development',
        'new construction', 'renovation', 'remodeling', 'home improvement',
        'general contractor', 'subcontractor', 'construction management',
        'building materials', 'construction software', 'project management',
        # === MARKET SEGMENTS ===
        'residential real estate', 'commercial real estate', 'industrial real estate',
        'luxury real estate', 'affordable housing', 'student housing',
        'senior housing', 'hospitality real estate', 'retail real estate',
        'mixed use', 'urban development', 'suburban development'
    ]

    # Cache duration in seconds
    CACHE_DURATION = 300  # 5 minutes

    def __init__(self):
        """Initialize scraper with sources."""
        self.sources = {
            # === RSS FEEDS (Easy to scrape) ===
            # Tech sources with PropTech coverage
            'techcrunch_main': 'https://techcrunch.com/feed/',
            # 'techcrunch_fintech': 'https://techcrunch.com/category/fintech/feed/',
            # 'venturebeat': 'https://venturebeat.com/feed/',
            # 'geekwire': 'https://www.geekwire.com/feed/',
            
            # Real estate industry RSS
            'inman': 'https://www.inman.com/feed/',
            # 'therealdeal': 'https://therealdeal.com/feed/',
            # 'constructiondive': 'https://www.constructiondive.com/feeds/news/',
            
            # Business/funding RSS
            'crunchbase_news': 'https://news.crunchbase.com/feed/',
            
            # === HTML SOURCES (More targeted) ===
            'propmodo': 'https://www.propmodo.com/',
            'proptechzone': 'https://www.proptechzone.com/',
            # 'metaprop_insights': 'https://www.metaprop.org/insights/',
        }
        self._cache = {}
        self._cache_timestamps = {}

    @lru_cache(maxsize=32)
    def _get_cached_content(self, url):
        """Get cached content if available and not expired."""
        if url in self._cache:
            timestamp = self._cache_timestamps.get(url, 0)
            if time.time() - timestamp < self.CACHE_DURATION:
                return self._cache[url]
        return None

    def _cache_content(self, url, content):
        """Cache content with timestamp."""
        self._cache[url] = content
        self._cache_timestamps[url] = time.time()

    async def _fetch_url(self, session, url, headers):
        """Fetch URL content asynchronously."""
        try:
            cached_content = self._get_cached_content(url)
            if cached_content:
                return cached_content
            async with session.get(url, headers=headers, timeout=10) as response:
                response.raise_for_status()
                content = await response.text()
                self._cache_content(url, content)
                return content
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return ''

    async def _scrape_rss_feed_async(self, feed_url: str, source_name: str, max_articles: int = 5) -> List[Dict[str, Any]]:
        """Scrape articles from an RSS feed with a limit using BeautifulSoup only."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/rss+xml, application/xml, text/xml, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(feed_url, headers=headers, timeout=10) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch RSS feed {feed_url} for {source_name}: {response.status}")
                        return []
                    content = await response.text()
                    soup = BeautifulSoup(content, 'xml')
                    items = soup.find_all('item')
                    logger.info(f"[DEBUG] {source_name}: Found {len(items)} <item> elements in RSS feed.")
                    items = items[:max_articles]
                    articles = []
                    for item in items:
                        title = item.find('title')
                        link = item.find('link')
                        description = item.find('description')
                        pub_date = item.find('pubDate')
                        article = {
                            'title': title.get_text() if title else '',
                            'url': link.get_text().strip() if link else '',
                            'link': link.get_text().strip() if link else '',
                            'published': pub_date.get_text() if pub_date else '',
                            'source': source_name,
                            'content': description.get_text() if description else ''
                        }
                        articles.append(article)
                    logger.info(f"[DEBUG] {source_name}: Extracted {len(articles)} articles from RSS feed.")
                    return articles
        except Exception as e:
            logger.error(f"Error scraping RSS feed {feed_url} for {source_name}: {str(e)}")
            return []

    async def _scrape_propmodo_async(self, session, max_articles=5):
        """Scrape Propmodo asynchronously."""
        try:
            url = self.sources['propmodo']
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            content = await self._fetch_url(session, url, headers)
            if not content:
                return []
            soup = BeautifulSoup(content, 'html.parser')
            articles = []
            article_selectors = [
                'a[href*="/news/"]',
                'a[href*="/article/"]', 
                'article a',
                '.post-title a',
                'h2 a',
                'h3 a'
            ]
            article_links = []
            for selector in article_selectors:
                links = soup.select(selector)
                if links:
                    article_links = links[:max_articles]
                    break
            if not article_links:
                return []
            for link in article_links:
                href = link.get('href') or ''
                title = link.get_text().strip() or ''
                if href:
                    if isinstance(href, str) and href.startswith('/'):
                        href = f"{url.rstrip('/')}{href}"
                    elif isinstance(href, str) and not href.startswith('http'):
                        href = f"{url.rstrip('/')}/{href}"
                article = {
                    'title': title,
                    'link': href,
                    'url': href,
                    'content': title,
                    'summary': title,
                    'published': '',
                    'source': 'propmodo'
                }
                articles.append(article)
            return articles
        except Exception as e:
            logger.error(f"Propmodo scraping failed: {str(e)}")
            return []

    async def _scrape_proptechzone_async(self, session, max_articles=5):
        """Scrape Proptechzone asynchronously."""
        try:
            url = self.sources['proptechzone']
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            content = await self._fetch_url(session, url, headers)
            if not content:
                return []
            soup = BeautifulSoup(content, 'html.parser')
            articles = []
            article_links = soup.select('a.card, a[href*="/companies/"]')[:max_articles]
            if not article_links:
                return []
            for link in article_links:
                href = link.get('href') or ''
                title = link.get_text().strip() or ''
                if href:
                    if isinstance(href, str) and href.startswith('/'):
                        href = f"{url.rstrip('/')}{href}"
                    elif isinstance(href, str) and not href.startswith('http'):
                        href = f"{url.rstrip('/')}/{href}"
                article = {
                    'title': title,
                    'link': href,
                    'url': href,
                    'content': title,
                    'summary': title,
                    'published': '',
                    'source': 'proptechzone'
                }
                articles.append(article)
            return articles
        except Exception as e:
            logger.error(f"Proptechzone scraping failed: {str(e)}")
            return []

    async def _scrape_all_sources_async(self, max_articles_per_source: int = 5) -> List[Dict[str, Any]]:
        """Scrape all sources with limits, using custom scrapers for HTML sources."""
        tasks = []
        for source_name, source_info in self.sources.items():
            if source_name == 'propmodo':
                tasks.append(self._scrape_propmodo_async(None, max_articles_per_source))
            elif source_name == 'proptechzone':
                tasks.append(self._scrape_proptechzone_async(None, max_articles_per_source))
            else:
                tasks.append(self._scrape_rss_feed_async(source_info, source_name, max_articles_per_source))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_articles = []
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            else:
                logger.error(f"Error in scraping task: {str(result)}")
        return all_articles

    def scrape_proptech_articles(self, max_articles: int = 5) -> List[Dict[str, Any]]:
        """Scrape PropTech articles with a limit, always returning at least 3 articles from any source if not enough match the filter."""
        try:
            articles = asyncio.run(self._scrape_all_sources_async(max_articles_per_source=3))
            filtered_articles = []
            non_matching_articles = []
            
            for article in articles:
                if self.is_proptech_relevant(article['title'] + ' ' + article['content']):
                    filtered_articles.append(article)
                else:
                    non_matching_articles.append(article)
                if len(filtered_articles) >= max_articles:
                    break
            # If not enough filtered, fill with non-matching articles
            if len(filtered_articles) < 3:
                needed = 3 - len(filtered_articles)
                filtered_articles.extend(non_matching_articles[:needed])
            # Always return at least 3, up to max_articles
            return filtered_articles[:max(max_articles, 3)]
        except Exception as e:
            logger.error(f"Error in scrape_proptech_articles: {str(e)}")
            return []

    def _clean_html_entities(self, text):
        """Clean HTML entities from text."""
        return html.unescape(text) if text else ''

    def _extract_rss_content(self, item):
        """Extract content from RSS item."""
        content = item.find('content:encoded')
        if content is None:
            content = item.find('description')
        return self._clean_html_entities(content.get_text() if content else '')

    def is_proptech_relevant(self, text):
        """Check if text is relevant to PropTech."""
        if not text:
            return False
        
        text = text.lower()
        score = 0
        
        for keyword in self.PROPTECH_KEYWORDS:
            if keyword.lower() in text:
                score += 1
                if score >= 1:  # Require at least 1 keyword match
                    return True
        
        return False

    def scrape_all_sources(self, max_articles_per_source=3):
        """Synchronous wrapper for async scraping."""
        return asyncio.run(self._scrape_all_sources_async(max_articles_per_source))

    def scrape_rss_feed(self, source_name, max_articles=5):
        """Synchronous wrapper for async RSS scraping."""
        return asyncio.run(self._scrape_rss_feed_async(self.sources[source_name], source_name, max_articles))

    def scrape_propmodo(self, max_articles=5):
        """Synchronous wrapper for async Propmodo scraping."""
        return asyncio.run(self._scrape_propmodo_async(None, max_articles))

    def _scrape_article_content(self, url):
        """Scrape full article content."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Get main content
            content = ''
            main_content = soup.find('main') or soup.find('article')
            if not main_content:
                main_content = soup.find('div', class_='content') or soup.find('div', class_='article')
            
            if main_content:
                content = main_content.get_text(separator=' ', strip=True)
            else:
                content = soup.get_text(separator=' ', strip=True)
            
            return content
            
        except Exception as e:
            logger.error(f"Error scraping article content from {url}: {str(e)}")
            return ''

    def scrape_built_in_real_estate(self, max_articles=5):
        """Synchronous wrapper for async Built In Real Estate scraping."""
        return asyncio.run(self._scrape_built_in_real_estate_async(None, max_articles))

    async def _scrape_built_in_real_estate_async(self, session, max_articles=5):
        """Scrape Built In Real Estate asynchronously."""
        try:
            url = 'https://builtin.com/real-estate'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            content = await self._fetch_url(session, url, headers)
            if not content:
                return []
            
            soup = BeautifulSoup(content, 'html.parser')
            articles = []
            
            # Find article elements
            article_elements = soup.find_all('div', class_='article-card')[:max_articles]
            
            for element in article_elements:
                try:
                    title_elem = element.find('h2')
                    link_elem = element.find('a')
                    
                    if title_elem and link_elem:
                        article = {
                            'title': title_elem.get_text(strip=True),
                            'url': link_elem.get('href', ''),
                            'published': '',
                            'source': 'built_in_real_estate',
                            'content': title_elem.get_text(strip=True)
                        }
                        articles.append(article)
                except Exception as e:
                    logger.error(f"Error processing Built In Real Estate article: {str(e)}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"Built In Real Estate scraping failed: {str(e)}")
            return []

    async def scrape_html_source(self, url: str, source_name: str, max_articles: int = 5) -> List[Dict[str, Any]]:
        """Scrape articles from an HTML source with a limit."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch HTML source {url}: {response.status}")
                        return []
                    content = await response.text()
                    soup = BeautifulSoup(content, 'lxml')
                    # Use regex for class_
                    article_elements = soup.find_all(['article', 'div'], class_=re.compile(r'(article|post)', re.I))[:max_articles]
                    articles = []
                    for element in article_elements:
                        try:
                            title_elem = element.find(['h1', 'h2', 'h3'])
                            link_elem = element.find('a')
                            if title_elem and link_elem:
                                article = {
                                    'title': title_elem.get_text(strip=True),
                                    'url': link_elem.get('href', ''),
                                    'published': '',  # HTML sources might not have this
                                    'source': source_name,
                                    'content': element.get_text(strip=True)[:500]  # Limit content length
                                }
                                articles.append(article)
                        except Exception as e:
                            logger.error(f"Error processing HTML article: {str(e)}")
                            continue
                    return articles
        except Exception as e:
            logger.error(f"Error scraping HTML source {url}: {str(e)}")
            return [] 