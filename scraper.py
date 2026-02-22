import requests
from bs4 import BeautifulSoup
import os
import urllib.request


class ElPaisScraper:

    BASE_URL = "https://elpais.com/opinion/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0"
        })

    def scrape_opinion_articles(self, limit=5):
        """Scrape first N articles from El País Opinion"""
        response = self.session.get(self.BASE_URL)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = []
        
        # Try multiple selectors to find article links
        cards = soup.select("article")[:limit]
        
        # If no articles found, try other common selectors
        if not cards:
            cards = soup.select(".article, .story, [class*='article'], .headline")
            cards = cards[:limit]
        
        # Also try to find links in opinion section
        if not cards:
            cards = soup.select("a[href*='/opinion/']")[:limit]

        for card in cards:
            try:
                title = None
                url = None
                
                # Try h2 a first
                title_tag = card.select_one("h2 a")
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    href = title_tag.get("href", "")
                    url = "https://elpais.com" + href if href.startswith("/") else href
                
                # Try h3 a
                if not title:
                    title_tag = card.select_one("h3 a")
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                        href = title_tag.get("href", "")
                        url = "https://elpais.com" + href if href.startswith("/") else href
                
                # Try direct anchor
                if not title:
                    title_tag = card.find("a")
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                        href = title_tag.get("href", "")
                        url = "https://elpais.com" + href if href.startswith("/") else href
                
                # Try getting title from h2, h3, h4 directly
                if not title:
                    title_elem = card.select_one("h2, h3, h4, h1")
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                
                # Skip if we couldn't find a valid title
                if not title or len(title) < 5:
                    continue
                    
                # Skip if we don't have a valid URL
                if not url or not url.startswith("http"):
                    continue

                article_data = self.scrape_article(url)
                # Use the title from the list page
                article_data["title"] = title
                articles.append(article_data)

                if len(articles) >= limit:
                    break

            except Exception:
                continue

        return articles

    def scrape_article(self, url):
        """Scrape a single El País article"""
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.select_one("h1").get_text(strip=True)
        author = soup.select_one("a[rel='author']")
        author = author.get_text(strip=True) if author else "Unknown"
        date = soup.select_one("time")
        date = date.get_text(strip=True) if date else "Unknown"

        paragraphs = soup.select("p")
        content = "\n".join([p.get_text(strip=True) for p in paragraphs])

        # Try multiple selectors to find the cover image
        image_url = None
        
        # Try article header image first
        image_tag = soup.select_one("article header img")
        if image_tag:
            image_url = image_tag.get("src") or image_tag.get("data-src")
        
        # Try figure picture img
        if not image_url:
            image_tag = soup.select_one("figure picture img")
            if image_tag:
                image_url = image_tag.get("src") or image_tag.get("data-src")
        
        # Try og:image meta tag
        if not image_url:
            og_image = soup.select_one("meta[property='og:image']")
            if og_image:
                image_url = og_image.get("content")
        
        # Try twitter:image meta tag
        if not image_url:
            twitter_image = soup.select_one("meta[name='twitter:image']")
            if twitter_image:
                image_url = twitter_image.get("content")
        
        # Try article body img
        if not image_url:
            image_tag = soup.select_one("article img")
            if image_tag:
                image_url = image_tag.get("src") or image_tag.get("data-src")
        
        # Try any img with srcset
        if not image_url:
            image_tag = soup.select_one("img[srcset]")
            if image_tag:
                srcset = image_tag.get("srcset", "")
                if srcset:
                    image_url = srcset.split(",")[0].strip().split(" ")[0]
        
        # Last resort - any large image
        if not image_url:
            image_tag = soup.select_one("img")
            if image_tag:
                image_url = image_tag.get("src")

        return {
            "title": title,
            "author": author,
            "date": date,
            "content": content,
            "article_url": url,
            "image_url": image_url
        }

    def download_image(self, url, save_path):
        try:
            urllib.request.urlretrieve(url, save_path)
            return True
        except:
            return False


def create_downloads_folder():
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    return "downloads"
