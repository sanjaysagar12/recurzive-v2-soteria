import networkx as nx
import numpy as np
import random
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib

class OriginTracer:
    def __init__(self):
        self.social_graph = nx.DiGraph()
        self.platforms = ['Twitter', 'Facebook', 'Instagram', 'YouTube', 'Reddit', 'TikTok']
        self.rumor_database = defaultdict(list)
    
    def trace_rumor_origin(self, content, suspect_accounts=None):
        """Enhanced origin tracing specifically for rumors"""
        content_hash = self._generate_content_hash(content)
        
        # Step 1: Identify potential origin points
        origin_candidates = self._identify_origin_candidates(content, suspect_accounts)
        
        # Step 2: Trace propagation path with timestamps
        propagation_path = self._trace_detailed_propagation(content, content_hash)
        
        # Step 3: Analyze network structure and influence
        network_analysis = self._analyze_influence_network(propagation_path)
        
        # Step 4: Identify key spreaders and amplifiers
        key_spreaders = self._identify_key_spreaders(propagation_path)
        
        return {
            'content_hash': content_hash,
            'origin_candidates': origin_candidates,
            'propagation_path': propagation_path,
            'network_analysis': network_analysis,
            'key_spreaders': key_spreaders,
            'trace_confidence': self._calculate_trace_confidence(origin_candidates, propagation_path),
            'recommended_actions': self._recommend_actions(origin_candidates, key_spreaders)
        }
    
    def trace_origin(self, content):
        """Standard origin tracing"""
        return self.trace_rumor_origin(content)
    
    def _generate_content_hash(self, content):
        """Generate unique hash for content tracking"""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _identify_origin_candidates(self, content, suspect_accounts):
        """Identify potential origin accounts"""
        candidates = []
        
        # Simulate analysis of posting patterns and timing
        potential_origins = [
            {'account': '@anonymous_source', 'platform': 'Twitter', 'confidence': 0.85, 'first_post': '2025-09-01 06:30:00'},
            {'account': 'suspicious_page', 'platform': 'Facebook', 'confidence': 0.72, 'first_post': '2025-09-01 07:15:00'},
            {'account': '@rumor_mill', 'platform': 'Instagram', 'confidence': 0.68, 'first_post': '2025-09-01 08:00:00'}
        ]
        
        if suspect_accounts:
            for account in suspect_accounts:
                potential_origins.append({
                    'account': account,
                    'platform': 'Twitter',
                    'confidence': random.uniform(0.6, 0.9),
                    'first_post': (datetime.now() - timedelta(hours=random.randint(2, 48))).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return sorted(potential_origins, key=lambda x: x['confidence'], reverse=True)
    
    def _trace_detailed_propagation(self, content, content_hash):
        """Trace detailed propagation with engagement metrics"""
        path = []
        
        # Simulate detailed propagation tracking
        hops = [
            {
                'hop': 0,
                'platform': 'Twitter',
                'account': '@origin_account',
                'timestamp': '2025-09-01 06:30:00',
                'engagement': 150,
                'reach': 5000,
                'account_type': 'anonymous'
            },
            {
                'hop': 1,
                'platform': 'Facebook',
                'account': 'viral_news_page',
                'timestamp': '2025-09-01 09:15:00',
                'engagement': 2500,
                'reach': 50000,
                'account_type': 'news_aggregator'
            },
            {
                'hop': 2,
                'platform': 'Instagram',
                'account': '@influencer_account',
                'timestamp': '2025-09-01 14:20:00',
                'engagement': 15000,
                'reach': 200000,
                'account_type': 'influencer'
            },
            {
                'hop': 3,
                'platform': 'Twitter',
                'account': '@verified_news',
                'timestamp': '2025-09-01 18:45:00',
                'engagement': 50000,
                'reach': 1000000,
                'account_type': 'media'
            }
        ]
        
        return hops
    
    def _analyze_influence_network(self, propagation_path):
        """Analyze the influence network structure"""
        # Create network graph
        G = nx.DiGraph()
        
        for i, hop in enumerate(propagation_path):
            G.add_node(hop['account'], 
                      platform=hop['platform'],
                      reach=hop['reach'],
                      engagement=hop['engagement'])
            
            if i > 0:
                G.add_edge(propagation_path[i-1]['account'], hop['account'],
                          time_diff=self._calculate_time_diff(propagation_path[i-1]['timestamp'], hop['timestamp']))
        
        # Calculate network metrics
        centrality = nx.betweenness_centrality(G)
        pagerank = nx.pagerank(G)
        
        return {
            'total_nodes': G.number_of_nodes(),
            'total_edges': G.number_of_edges(),
            'network_density': nx.density(G),
            'centrality_scores': centrality,
            'influence_scores': pagerank,
            'network_visualization': self._generate_network_viz(G)
        }
    
    def _identify_key_spreaders(self, propagation_path):
        """Identify accounts that significantly amplified the rumor"""
        key_spreaders = []
        
        for hop in propagation_path:
            if hop['engagement'] > 10000 or hop['reach'] > 100000:
                risk_level = 'high' if hop['reach'] > 500000 else 'medium'
                key_spreaders.append({
                    'account': hop['account'],
                    'platform': hop['platform'],
                    'reach': hop['reach'],
                    'engagement': hop['engagement'],
                    'risk_level': risk_level,
                    'account_type': hop['account_type']
                })
        
        return sorted(key_spreaders, key=lambda x: x['reach'], reverse=True)
    
    def _calculate_time_diff(self, time1, time2):
        """Calculate time difference between posts"""
        t1 = datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
        t2 = datetime.strptime(time2, '%Y-%m-%d %H:%M:%S')
        return abs((t2 - t1).total_seconds() / 3600)  # Return hours
    
    def _generate_network_viz(self, graph):
        """Generate network visualization data"""
        pos = nx.spring_layout(graph, k=1, iterations=50)
        
        nodes = []
        edges = []
        
        for node in graph.nodes():
            nodes.append({
                'id': node,
                'x': pos[node][0] * 10,
                'y': pos[node][1] * 10,
                'size': min(graph.nodes[node].get('reach', 1000) / 10000, 20),
                'color': self._get_node_color(graph.nodes[node].get('platform'))
            })
        
        for edge in graph.edges():
            edges.append({
                'source': edge[0],
                'target': edge[1],
                'weight': graph.edges[edge].get('time_diff', 1)
            })
        
        return {'nodes': nodes, 'edges': edges}
    
    def _get_node_color(self, platform):
        """Get color based on platform"""
        colors = {
            'Twitter': '#1DA1F2',
            'Facebook': '#4267B2',
            'Instagram': '#E4405F',
            'YouTube': '#FF0000',
            'Reddit': '#FF4500',
            'TikTok': '#000000'
        }
        return colors.get(platform, '#808080')
    
    def _calculate_trace_confidence(self, origin_candidates, propagation_path):
        """Calculate confidence in the origin trace"""
        if not origin_candidates or not propagation_path:
            return 0.0
        
        # Factors affecting confidence
        origin_confidence = max([c['confidence'] for c in origin_candidates])
        path_completeness = min(len(propagation_path) / 5, 1.0)  # Ideal path length
        temporal_consistency = self._check_temporal_consistency(propagation_path)
        
        overall_confidence = (origin_confidence * 0.4 + 
                            path_completeness * 0.3 + 
                            temporal_consistency * 0.3)
        
        return round(overall_confidence, 3)
    
    def _check_temporal_consistency(self, propagation_path):
        """Check if timestamps make sense"""
        if len(propagation_path) < 2:
            return 1.0
        
        consistent = True
        for i in range(1, len(propagation_path)):
            prev_time = datetime.strptime(propagation_path[i-1]['timestamp'], '%Y-%m-%d %H:%M:%S')
            curr_time = datetime.strptime(propagation_path[i]['timestamp'], '%Y-%m-%d %H:%M:%S')
            
            if curr_time <= prev_time:
                consistent = False
                break
        
        return 1.0 if consistent else 0.5
    
    def _recommend_actions(self, origin_candidates, key_spreaders):
        """Recommend actions based on trace results"""
        actions = []
        
        # Actions for origin accounts
        if origin_candidates:
            top_origin = origin_candidates[0]
            if top_origin['confidence'] > 0.8:
                actions.append({
                    'type': 'investigate_origin',
                    'target': top_origin['account'],
                    'platform': top_origin['platform'],
                    'priority': 'high',
                    'action': 'Deep investigation of account activity and connections'
                })
        
        # Actions for key spreaders
        for spreader in key_spreaders[:3]:  # Top 3 spreaders
            if spreader['risk_level'] == 'high':
                actions.append({
                    'type': 'monitor_spreader',
                    'target': spreader['account'],
                    'platform': spreader['platform'],
                    'priority': 'medium',
                    'action': f'Monitor account for future misinformation (Reach: {spreader["reach"]:,})'
                })
        
        return actions
