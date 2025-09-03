from datetime import datetime
import random

class ViralTracker:
    def __init__(self):
        self.viral_threshold = 10000

    def track_viral_content(self, posts):
        viral_posts = []
        for post in posts:
            engagement = post.get('engagement', 0)
            if engagement > self.viral_threshold:
                viral_score = self._calculate_viral_score(post)
                viral_posts.append({
                    'post_id': post.get('id'),
                    'platform': post.get('platform'),
                    'content': post.get('content', ''),
                    'engagement': engagement,
                    'viral_score': viral_score,
                    'timestamp': post.get('timestamp'),
                    'velocity': self._calculate_spread_velocity(post)
                })
        return sorted(viral_posts, key=lambda x: x['viral_score'], reverse=True)

    def _calculate_viral_score(self, post):
        engagement = post.get('engagement', 0)
        base_score = min(engagement / 100000, 1.0)
        timestamp = post.get('timestamp', datetime.now())
        try:
            if isinstance(timestamp, str):
                post_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                post_time = timestamp
            hours_ago = (datetime.now() - post_time).total_seconds() / 3600
            recency_boost = max(0, 1 - (hours_ago / 24))
        except:
            recency_boost = 0
        return min(base_score + recency_boost * 0.2, 1.0)

    def _calculate_spread_velocity(self, post):
        engagement = post.get('engagement', 0)
        return random.uniform(0.5, 2.0) * (engagement / 10000)
