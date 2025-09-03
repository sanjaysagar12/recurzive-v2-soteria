import requests
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv
import time
import re
import random

load_dotenv()

class RealSocialMonitor:
    def __init__(self):
        # Initialize attributes first to avoid AttributeError
        self.twitter_client = None
        self.reddit = None
        
        self.setup_twitter_api()
        self.setup_reddit_api()
        
    def setup_twitter_api(self):
        """Setup Twitter API"""
        try:
            consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
            consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            
            if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
                print("⚠️ Twitter credentials missing. Using demo data.")
                self.twitter_client = None
                return
                
            # Try to import tweepy and setup
            try:
                import tweepy
                auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
                auth.set_access_token(access_token, access_token_secret)
                self.twitter_client = tweepy.API(auth, wait_on_rate_limit=True)
                
                # Test connection
                self.twitter_client.verify_credentials()
                print("✅ Twitter API connected successfully")
                
            except ImportError:
                print("⚠️ Tweepy not installed. Using demo data.")
                self.twitter_client = None
            except Exception as e:
                print(f"❌ Twitter API test failed: {e}")
                self.twitter_client = None
                
        except Exception as e:
            print(f"❌ Twitter API setup failed: {e}")
            self.twitter_client = None
    
    def setup_reddit_api(self):
        """Setup Reddit API"""
        try:
            import praw
            
            client_id = os.getenv('REDDIT_CLIENT_ID')
            client_secret = os.getenv('REDDIT_CLIENT_SECRET')
            user_agent = os.getenv('REDDIT_USER_AGENT', 'MisinfoDetector/1.0')
            
            if not client_id or not client_secret:
                print("⚠️ Reddit credentials not found. Using demo data.")
                self.reddit = None
                return
            
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            
            # Test connection
            self.reddit.user.me()
            print("✅ Reddit API connected successfully")
                
        except Exception as e:
            print(f"❌ Reddit API setup failed: {e}")
            self.reddit = None
    
    def get_real_twitter_posts(self, vip_accounts, keywords, max_results=50):
        """Get real tweets from VIP accounts"""
        # Check if twitter_client exists and is not None
        if not hasattr(self, 'twitter_client') or not self.twitter_client:
            return self._get_realistic_demo_data(vip_accounts, keywords)
        
        all_tweets = []
        
        for account in vip_accounts:
            try:
                username = account.replace('@', '')
                
                tweets = self.twitter_client.user_timeline(
                    screen_name=username,
                    count=min(max_results, 100),
                    include_rts=False,
                    exclude_replies=True
                )
                
                for tweet in tweets:
                    if any(keyword.lower() in tweet.text.lower() for keyword in keywords):
                        all_tweets.append({
                            'id': tweet.id,
                            'username': f'@{username}',
                            'platform': 'Twitter',
                            'content': tweet.text,
                            'timestamp': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'engagement': tweet.favorite_count + tweet.retweet_count,
                            'likes': tweet.favorite_count,
                            'retweets': tweet.retweet_count,
                            'url': f"https://twitter.com/{username}/status/{tweet.id}",
                            'source': 'Real API'
                        })
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error fetching tweets for {account}: {e}")
                continue
        
        if not all_tweets:
            return self._get_realistic_demo_data(vip_accounts, keywords)
        
        return sorted(all_tweets, key=lambda x: x['timestamp'], reverse=True)
    
    def get_real_reddit_posts(self, subreddits, keywords, max_results=50):
        """Get real Reddit posts"""
        if not hasattr(self, 'reddit') or not self.reddit:
            return self._get_demo_reddit_posts(subreddits, keywords)
        
        all_posts = []
        
        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                for submission in subreddit.hot(limit=max_results):
                    text_to_search = f"{submission.title} {submission.selftext}".lower()
                    
                    if any(keyword.lower() in text_to_search for keyword in keywords):
                        all_posts.append({
                            'id': submission.id,
                            'username': f'u/{submission.author.name if submission.author else "deleted"}',
                            'platform': 'Reddit',
                            'subreddit': subreddit_name,
                            'title': submission.title,
                            'content': submission.selftext[:500] + "..." if len(submission.selftext) > 500 else submission.selftext,
                            'timestamp': datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                            'engagement': submission.score,
                            'upvotes': submission.ups,
                            'comments': submission.num_comments,
                            'url': f"https://reddit.com{submission.permalink}",
                            'source': 'Real API'
                        })
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Error fetching Reddit posts for r/{subreddit_name}: {e}")
                continue
        
        return sorted(all_posts, key=lambda x: x['timestamp'], reverse=True)
    
    def _get_realistic_demo_data(self, vip_accounts, keywords):
        """Generate highly realistic VIP posts for demo"""
        realistic_content = {
            '@elonmusk': [
                "Tesla FSD Beta 12.0 rolling out to more users. The improvements are significant. Full self-driving is closer than ever.",
                "SpaceX Starship IFT-4 preparations underway. Next month we attempt orbital refueling. Historic moment ahead.",
                "Neuralink patient update: remarkable progress in brain-computer interface. The future is becoming reality.",
                "X (Twitter) usage at all-time highs. Free speech platform thriving despite advertiser boycotts.",
                "Working 16-hour days at Gigafactory Texas. Model Y production hitting new records."
            ],
            '@JoeBiden': [
                "Inflation continues to cool as our economic policies take effect. America is stronger than ever.",
                "Meeting with NATO allies tomorrow to discuss Ukraine support. Democracy will prevail.",
                "Our infrastructure investments are creating millions of jobs nationwide. Building back better works.",
                "Climate action cannot wait. America is leading the global transition to clean energy.",
                "Healthcare costs are finally coming down thanks to our prescription drug reforms."
            ],
            '@BillGates': [
                "Gates Foundation malaria initiative shows 40% reduction in deaths. Science and data save lives.",
                "AI developments in education are transformative. Every child deserves personalized learning.",
                "Climate innovation funding reaching $2B this year. Technology will solve the climate crisis.",
                "Vaccine equity remains critical. No one is safe until everyone is safe.",
                "Meeting with world leaders on pandemic preparedness. We cannot repeat COVID-19 mistakes."
            ]
        }
        
        all_posts = []
        for account in vip_accounts:
            account_posts = realistic_content.get(account, [
                f"Important update about {random.choice(keywords)} from {account}",
                f"Breakthrough news regarding {random.choice(keywords)}",
                f"My thoughts on recent {random.choice(keywords)} developments"
            ])
            
            for i, content in enumerate(account_posts[:3]):
                if any(keyword.lower() in content.lower() for keyword in keywords):
                    all_posts.append({
                        'id': f"demo_{account}_{i}",
                        'username': account,
                        'platform': 'Twitter',
                        'content': content,
                        'timestamp': (datetime.now() - timedelta(hours=i*2)).strftime('%Y-%m-%d %H:%M:%S'),
                        'engagement': random.randint(50000, 1000000),
                        'likes': random.randint(20000, 500000),
                        'retweets': random.randint(5000, 100000),
                        'replies': random.randint(1000, 50000),
                        'url': f"https://twitter.com{account}/status/{random.randint(1000000000000000000, 9999999999999999999)}",
                        'verified': True,
                        'source': 'Realistic Demo'
                    })
        
        return all_posts
    
    def _get_demo_reddit_posts(self, subreddits, keywords):
        """Fallback demo data for Reddit"""
        demo_posts = []
        for subreddit in subreddits:
            for i, keyword in enumerate(keywords[:2]):
                demo_posts.append({
                    'id': f"demo_{subreddit}_{i}",
                    'username': f'u/demo_user_{i}',
                    'platform': 'Reddit', 
                    'subreddit': subreddit,
                    'title': f"Discussion about {keyword} in r/{subreddit}",
                    'content': f"Demo Reddit post content about {keyword} - API credentials needed for real data",
                    'timestamp': (datetime.now() - timedelta(hours=i+1)).strftime('%Y-%m-%d %H:%M:%S'),
                    'engagement': random.randint(10, 1000),
                    'upvotes': random.randint(5, 500),
                    'comments': random.randint(1, 100),
                    'url': f"https://reddit.com/r/{subreddit}/comments/demo",
                    'source': 'Demo'
                })
        
        return demo_posts
