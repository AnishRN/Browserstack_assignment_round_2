"""
El País Article Scraper & Analyzer - Console Version
Single file that runs directly and prints results to console
"""

import requests
from bs4 import BeautifulSoup
import re
import string
from collections import Counter



class ElPaisScraper:
    BASE_URL = "https://elpais.com/opinion/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def scrape_opinion_articles(self, limit=5):
        """Scrape first N articles from El País Opinion"""
        print(f"\n{'='*60}")
        print(f"SCRAPING ARTICLES FROM EL PAÍS OPINION")
        print(f"{'='*60}")
        print(f"Fetching from: {self.BASE_URL}")
        print(f"Limit: {limit} articles\n")
        
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

            except Exception as e:
                continue

        return articles

    def scrape_article(self, url):
        """Scrape a single El País article"""
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.select_one("h1")
        title = title.get_text(strip=True) if title else "Unknown"
        
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


class MyMemoryTranslator:
    API_URL = "https://api.mymemory.translated.net/get"

    def translate(self, text, target="en"):
        params = {
            "q": text,
            "langpair": f"es|{target}"
        }
        try:
            r = requests.get(self.API_URL, params=params)
            data = r.json()
            return data["responseData"]["translatedText"]
        except Exception as e:
            print(f"Translation error: {e}")
            return text

    def translate_batch(self, texts):
        return [self.translate(t) for t in texts]


def clean_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_words(text):
    stop_words = {"the", "and", "is", "are", "to", "in", "on", "de", "la", "el", "que", 
                  "of", "for", "with", "by", "a", "an", "as", "at", "from", "it", "that",
                  "this", "be", "has", "have", "was", "were", "but", "or", "not", "so"}
    words = clean_text(text).split()
    return [w for w in words if len(w) > 2 and w not in stop_words]


def analyze_word_frequency(headers):
    all_words = []
    for h in headers:
        all_words.extend(extract_words(h))
    return Counter(all_words)


def find_repeated_words(headers, min_count=2):
    freq = analyze_word_frequency(headers)
    return {w: c for w, c in freq.items() if c > min_count}


def get_top_words(headers, n=10):
    freq = analyze_word_frequency(headers)
    return freq.most_common(n)


def print_articles(articles):
    """Print scraped articles in a formatted way"""
    print(f"\n{'='*60}")
    print(f"SCRAPED ARTICLES")
    print(f"{'='*60}\n")
    
    for i, article in enumerate(articles, 1):
        print(f"--- Article {i} ---")
        print(f"Title: {article['title']}")
        print(f"Author: {article['author']}")
        print(f"Date: {article['date']}")
        print(f"URL: {article['article_url']}")
        print(f"Image: {article['image_url'] if article['image_url'] else 'N/A'}")
        # Print first 200 chars of content
        content_preview = article['content'][:200] + "..." if len(article['content']) > 200 else article['content']
        print(f"Content Preview: {content_preview}")
        print()


def print_translations(articles, translations):
    """Print translated titles"""
    print(f"\n{'='*60}")
    print(f"TRANSLATED TITLES (Spanish → English)")
    print(f"{'='*60}\n")
    
    for i, (article, translation) in enumerate(zip(articles, translations), 1):
        print(f"--- Article {i} ---")
        print(f"Original (Spanish): {article['title']}")
        print(f"Translated (English): {translation}")
        print()


def print_word_analysis(translated_titles):
    """Print word frequency analysis"""
    print(f"\n{'='*60}")
    print(f"WORD FREQUENCY ANALYSIS")
    print(f"{'='*60}\n")
    
    # Top words
    top_words = get_top_words(translated_titles, n=10)
    print("Top 10 Most Common Words:")
    print("-" * 30)
    for word, count in top_words:
        print(f"  {word:<20} : {count}")
    
    # Repeated words (appearing more than twice)
    repeated = find_repeated_words(translated_titles, min_count=2)
    print(f"\nRepeated Words (appearing more than twice):")
    print("-" * 30)
    if repeated:
        for word, count in sorted(repeated.items(), key=lambda x: x[1], reverse=True):
            print(f"  {word:<20} : {count}")
    else:
        print("  No words repeated more than twice")
    
    # Full frequency table
    full_freq = analyze_word_frequency(translated_titles)
    print(f"\nComplete Word Frequency Table:")
    print("-" * 30)
    for word, count in sorted(full_freq.items(), key=lambda x: x[1], reverse=True):
        print(f"  {word:<20} : {count}")


def print_summary(articles, translations):
    """Print summary statistics"""
    print(f"\n{'='*60}")
    print(f"SUMMARY STATISTICS")
    print(f"{'='*60}\n")
    
    print(f"Total Articles Scraped: {len(articles)}")
    print(f"Total Titles Translated: {len(translations)}")
    
    # Calculate total content length
    total_content = sum(len(a['content']) for a in articles)
    print(f"Total Content Characters: {total_content:,}")
    
    # Average title length
    avg_title_len = sum(len(a['title']) for a in articles) / len(articles) if articles else 0
    print(f"Average Title Length: {avg_title_len:.1f} characters")
    
    # Authors
    authors = set(a['author'] for a in articles if a['author'] != "Unknown")
    print(f"Unique Authors: {len(authors)}")
    if authors:
        print(f"Authors: {', '.join(list(authors)[:5])}")


def main():
    """Main function to run the console application"""
    print("\n" + "="*60)
    print("EL PAÍS ARTICLE SCRAPER & ANALYZER - CONSOLE VERSION")
    print("="*60)
    print("\nThis program will:")
    print("1. Scrape articles from El País Opinion section")
    print("2. Translate Spanish titles to English")
    print("3. Analyze word frequency in translated titles")
    print("4. Display all results in the console\n")
    
    # Configuration
    NUM_ARTICLES = 5
    
    # Initialize components
    scraper = ElPaisScraper()
    translator = MyMemoryTranslator()
    
    # Step 1: Scrape articles
    articles = scraper.scrape_opinion_articles(limit=NUM_ARTICLES)
    
    if not articles:
        print("No articles found! The website structure may have changed.")
        return
    
    # Print scraped articles
    print_articles(articles)
    
    # Step 2: Translate titles
    print(f"\n{'='*60}")
    print(f"TRANSLATING TITLES")
    print(f"{'='*60}\n")
    print("Translating Spanish titles to English using MyMemory API...\n")
    
    spanish_titles = [article['title'] for article in articles]
    translations = translator.translate_batch(spanish_titles)
    
    # Print translations
    print_translations(articles, translations)
    
    # Step 3: Analyze words
    print_word_analysis(translations)
    
    # Step 4: Summary
    print_summary(articles, translations)
    
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
