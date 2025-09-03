import streamlit as st
import pandas as pd
import plotly.express as px
from backend.social_monitor import RealSocialMonitor
from backend.fact_checker import RealFactChecker
from datetime import datetime
import os

@st.cache_resource
def load_real_components():
    return {
        'social_monitor': RealSocialMonitor(),
        'fact_checker': RealFactChecker()
    }

def render():
    st.title("🔍 Real-Time Misinformation Detection")
    
    # Check API status
    with st.sidebar:
        st.markdown("### 🔧 API Status")
        
        # API setup instructions
        if not os.getenv('TWITTER_BEARER_TOKEN'):
            st.error("❌ Twitter API not configured")
            with st.expander("Setup Twitter API"):
                st.markdown("""
                1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
                2. Create an app and get Bearer Token
                3. Add to .env file: `TWITTER_BEARER_TOKEN=your_token`
                """)
        else:
            st.success("✅ Twitter API configured")
        
        if not os.getenv('REDDIT_CLIENT_ID'):
            st.error("❌ Reddit API not configured")
            with st.expander("Setup Reddit API"):
                st.markdown("""
                1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
                2. Create an app and get credentials
                3. Add to .env file:
                   ```
                   REDDIT_CLIENT_ID=your_id
                   REDDIT_CLIENT_SECRET=your_secret
                   ```
                """)
        else:
            st.success("✅ Reddit API configured")
    
    components = load_real_components()
    
    tab1, tab2, tab3 = st.tabs(["🎯 Live Scanning", "📊 Analysis", "🔍 Manual Check"])
    
    with tab1:
        st.header("Live Social Media Scanning")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # VIP accounts to monitor
            vip_accounts = st.multiselect(
                "VIP Accounts (Twitter):",
                ["@elonmusk", "@JoeBiden", "@realDonaldTrump", "@Oprah", "@BillGates"],
                default=["@elonmusk"]
            )
            
            # Reddit subreddits
            subreddits = st.multiselect(
                "Reddit Communities:",
                ["news", "politics", "worldnews", "technology", "conspiracy"],
                default=["news"]
            )
            
            # Keywords
            keywords = st.text_input(
                "Alert Keywords:",
                "breaking, exclusive, leaked, confirmed, denied"
            ).split(", ")
            
            # Scan button
            if st.button("🔴 Start Live Scan", type="primary"):
                with st.spinner("Scanning social media..."):
                    
                    # Get real Twitter data
                    twitter_posts = components['social_monitor'].get_real_twitter_posts(
                        vip_accounts, keywords, max_results=20
                    )
                    
                    # Get real Reddit data
                    reddit_posts = components['social_monitor'].get_real_reddit_posts(
                        subreddits, keywords, max_results=20
                    )
                    
                    # Combine and analyze
                    all_posts = twitter_posts + reddit_posts
                    
                    # Analyze each post for misinformation
                    analyzed_posts = []
                    for post in all_posts:
                        analysis = components['fact_checker'].analyze_misinformation(
                            post['content']
                        )
                        post['misinformation_score'] = analysis['misinformation_probability']
                        post['verdict'] = analysis['verdict']
                        post['flags'] = analysis['flags']
                        analyzed_posts.append(post)
                    
                    st.session_state.analyzed_posts = sorted(
                        analyzed_posts, 
                        key=lambda x: x['misinformation_score'], 
                        reverse=True
                    )
        
        with col2:
            st.subheader("🚨 Real-Time Results")
            
            if 'analyzed_posts' in st.session_state:
                for post in st.session_state.analyzed_posts[:10]:
                    
                    # Color-coded risk level
                    risk_score = post['misinformation_score']
                    if risk_score >= 0.7:
                        risk_color = "🔴"
                        risk_level = "HIGH RISK"
                    elif risk_score >= 0.5:
                        risk_color = "🟡"
                        risk_level = "MEDIUM RISK"
                    else:
                        risk_color = "🟢"
                        risk_level = "LOW RISK"
                    
                    with st.expander(f"{risk_color} {risk_level} - {post['platform']} - {post['username']}"):
                        st.markdown(f"**Content:** {post['content'][:200]}...")
                        st.markdown(f"**Verdict:** {post['verdict']}")
                        st.markdown(f"**Risk Score:** {risk_score:.2%}")
                        
                        if post['flags']:
                            st.markdown(f"**Warning Flags:** {', '.join(post['flags'])}")
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown(f"**Engagement:** {post['engagement']}")
                            st.markdown(f"**Time:** {post['timestamp']}")
                        
                        with col_b:
                            if 'url' in post and post['url'] != '#':
                                st.markdown(f"[🔗 View Original]({post['url']})")
                            
                            if st.button(f"📝 Report This", key=f"report_{post.get('id', 'unknown')}"):
                                st.success("Report functionality would be triggered here")
            
            else:
                st.info("Click 'Start Live Scan' to begin monitoring")
    
    with tab2:
        st.header("📊 Detection Analytics")
        
        if 'analyzed_posts' in st.session_state:
            posts_df = pd.DataFrame(st.session_state.analyzed_posts)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Risk distribution
                risk_counts = posts_df['verdict'].value_counts()
                fig = px.pie(
                    values=risk_counts.values,
                    names=risk_counts.index,
                    title="Risk Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Platform comparison
                platform_risk = posts_df.groupby('platform')['misinformation_score'].mean()
                fig = px.bar(
                    x=platform_risk.index,
                    y=platform_risk.values,
                    title="Average Risk by Platform"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Detailed table
            st.subheader("📋 Detailed Results")
            display_df = posts_df[[
                'platform', 'username', 'content', 'misinformation_score', 
                'verdict', 'engagement', 'timestamp'
            ]].copy()
            display_df['content'] = display_df['content'].str[:100] + "..."
            display_df['misinformation_score'] = display_df['misinformation_score'].round(3)
            
            st.dataframe(display_df, use_container_width=True)
        
        else:
            st.info("No analysis data available. Run a live scan first.")
    
    with tab3:
        st.header("🔍 Manual Fact Check")
        
        text_to_check = st.text_area(
            "Enter text to analyze:",
            height=150,
            placeholder="Paste suspicious content here..."
        )
        
        if st.button("🧠 Analyze Now", type="primary"):
            if text_to_check:
                with st.spinner("Analyzing content..."):
                    result = components['fact_checker'].analyze_misinformation(text_to_check)
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"### {result['verdict']}")
                        st.markdown(f"**Misinformation Probability:** {result['misinformation_probability']:.1%}")
                        st.markdown(f"**Confidence:** {result['confidence']:.1%}")
                        
                        if result['flags']:
                            st.warning(f"**Warning Flags:** {', '.join(result['flags'])}")
                        
                        # Detailed analysis
                        with st.expander("📋 Detailed Analysis"):
                            analysis = result['analysis']
                            st.json(analysis)
                    
                    with col2:
                        # Risk gauge
                        score = result['misinformation_probability']
                        color = "red" if score >= 0.7 else "orange" if score >= 0.5 else "green"
                        
                        st.metric("Risk Level", f"{score:.1%}")
                        
                        if score >= 0.7:
                            st.error("🚨 HIGH RISK")
                        elif score >= 0.5:
                            st.warning("⚠️ MEDIUM RISK")
                        else:
                            st.success("✅ LOW RISK")

def main():
    st.set_page_config(
        page_title="Real Misinformation Detector",
        page_icon="🔍",
        layout="wide"
    )
    render()

if __name__ == "__main__":
    main()
