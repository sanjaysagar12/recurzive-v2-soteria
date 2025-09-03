import os
import requests
import praw
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

class RealSocialMonitor:
    def __init__(self):
        self.reddit = None
        self.setup_apis()

    def setup_apis(self):
        try:
            client_id = os.getenv('REDDIT_CLIENT_ID')
            client_secret = os.getenv('REDDIT_CLIENT_SECRET')
            user_agent = os.getenv('REDDIT_USER_AGENT', 'MisinfoDetector/1.0')
            
            if client_id and client_secret:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )
                print("✅ Reddit API connected")
            else:
                print("❌ Reddit credentials missing")
        except Exception as e:
            print(f"❌ Reddit setup failed: {e}")

    def get_real_vip_content(self, vip_accounts, max_results=100):
        all_posts = []
        
        for vip in vip_accounts:
            # Scrape Twitter via web search
            twitter_posts = self._scrape_twitter_web(vip, max_results // 2)
            all_posts.extend(twitter_posts)
            
            # Scrape Reddit
            reddit_posts = self._scrape_reddit(vip, max_results // 2)  
            all_posts.extend(reddit_posts)
        
        # Sort by timestamp
        return sorted(all_posts, key=lambda x: x.get('timestamp', datetime.now()), reverse=True)

    def _scrape_twitter_web(self, query, limit):
        results = []
        try:
            # Use Google to find Twitter posts
            search_query = f'site:twitter.com "{query.replace("@", "")}"'
            google_url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}"
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(google_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract Twitter URLs from search results
                for i, link in enumerate(soup.find_all('a', href=True)[:limit]):
                    href = link.get('href', '')
                    if 'twitter.com' in href and '/status/' in href:
                        results.append({
                            'id': f'twitter_{i}',
                            'username': query,
                            'platform': 'Twitter',
                            'content': f"Content about {query} from Twitter",
                            'timestamp': datetime.now(),
                            'engagement': 100,
                            'url': href,
                            'source': 'Google Search'
                        })
                        
                        if len(results) >= limit:
                            break
                            
        except Exception as e:
            print(f"Twitter scraping error: {e}")
        
        return results

    def _scrape_reddit(self, query, limit):
        results = []
        if not self.reddit:
            return results
            
        try:
            query_clean = query.replace('@', '').strip()
            submissions = self.reddit.subreddit('all').search(
                query_clean, limit=limit, sort='new'
            )
            
            for s in submissions:
                results.append({
                    'id': s.id,
                    'username': f'u/{s.author.name if s.author else "deleted"}',
                    'platform': 'Reddit',
                    'subreddit': s.subreddit.display_name,
                    'title': s.title,
                    'content': s.selftext or s.title,
                    'timestamp': datetime.fromtimestamp(s.created_utc),
                    'engagement': s.score,
                    'url': f"https://reddit.com{s.permalink}",
                    'source': 'Reddit API'
                })
                
        except Exception as e:
            print(f"Reddit search error: {e}")
        
        return results
