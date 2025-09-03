import streamlit as st
import pandas as pd
import plotly.express as px
from backend.social_monitor import RealSocialMonitor
from backend.fact_checker import RealFactChecker
from backend.viral_tracker import ViralTracker
from backend.origin_tracer import RealOriginTracer
from datetime import datetime
import os

@st.cache_resource
def load_components():
    return {
        'social_monitor': RealSocialMonitor(),
        'fact_checker': RealFactChecker(),
        'viral_tracker': ViralTracker(),
        'origin_tracer': RealOriginTracer()
    }

def render():
    st.title("🔍 Real-Time VIP Misinformation Detection")
    
    # User input for VIP name
    vip_input = st.text_input("Enter VIP name or handle:", "@elonmusk", help="Enter any VIP handle or name to search for")
    
    # Advanced options
    with st.expander("🎯 Advanced Options"):
        max_posts = st.slider("Maximum posts per platform:", 10, 500, 50)
        min_engagement = st.slider("Minimum engagement threshold:", 0, 10000, 0)
        
    # Scan button
    if st.button("🚨 Start VIP Content Scan", type="primary"):
        if not vip_input.strip():
            st.error("Please enter a VIP name or handle")
            return
            
        components = load_components()
        
        with st.spinner(f"Scanning content about {vip_input}..."):
            # Get posts
            all_posts = components['social_monitor'].get_real_vip_content([vip_input], max_posts)
            
            # Filter by engagement
            filtered_posts = [p for p in all_posts if p.get('engagement', 0) >= min_engagement]
            
            if not filtered_posts:
                st.warning("No posts found meeting your criteria. Try lowering the engagement threshold.")
                return
            
            # Analyze posts
            analyzed_posts = []
            analysis_progress = st.progress(0)
            
            for i, post in enumerate(filtered_posts):
                content = post.get('content', '') or post.get('title', '')
                if content:
                    analysis = components['fact_checker'].analyze_real_content(content)
                    post['misinformation_score'] = analysis['misinformation_probability']
                    post['verdict'] = analysis['verdict']
                    post['flags'] = analysis.get('flags', [])
                else:
                    post['misinformation_score'] = 0.5
                    post['verdict'] = 'No Content'
                    post['flags'] = []
                
                analyzed_posts.append(post)
                analysis_progress.progress((i + 1) / len(filtered_posts))
            
            # Store in session state
            st.session_state.analyzed_posts = sorted(analyzed_posts, key=lambda x: x['misinformation_score'], reverse=True)
            
            st.success(f"✅ Analyzed {len(analyzed_posts)} posts")
    
    # Display results
    if 'analyzed_posts' in st.session_state and st.session_state.analyzed_posts:
        posts = st.session_state.analyzed_posts
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            high_risk = len([p for p in posts if p['misinformation_score'] >= 0.7])
            st.metric("🔴 High Risk", high_risk)
        with col2:
            medium_risk = len([p for p in posts if 0.5 <= p['misinformation_score'] < 0.7])
            st.metric("🟡 Medium Risk", medium_risk)
        with col3:
            low_risk = len([p for p in posts if p['misinformation_score'] < 0.5])
            st.metric("🟢 Low Risk", low_risk)
        with col4:
            total_engagement = sum(p.get('engagement', 0) for p in posts)
            st.metric("Total Engagement", f"{total_engagement:,}")
        
        # Show individual posts
        st.subheader("📊 Analyzed Posts")
        
        for i, post in enumerate(posts[:20]):  # Show top 20
            risk_score = post['misinformation_score']
            
            if risk_score >= 0.7:
                risk_emoji = "🔴"
                risk_text = "HIGH RISK"
            elif risk_score >= 0.5:
                risk_emoji = "🟡" 
                risk_text = "MEDIUM RISK"
            else:
                risk_emoji = "🟢"
                risk_text = "LOW RISK"
            
            with st.expander(f"{risk_emoji} {risk_text} - {post['platform']} ({risk_score:.1%})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Content:**")
                    content = post.get('content', '')[:300]
                    st.write(content + ("..." if len(post.get('content', '')) > 300 else ""))
                    
                    st.write(f"**Platform:** {post['platform']}")
                    st.write(f"**Username:** {post['username']}")
                    st.write(f"**Verdict:** {post['verdict']}")
                    
                    if post.get('flags'):
                        st.write(f"**Flags:** {', '.join(post['flags'])}")
                
                with col2:
                    st.metric("Risk Score", f"{risk_score:.1%}")
                    st.metric("Engagement", f"{post.get('engagement', 0):,}")
                    
                    if post.get('url'):
                        st.markdown(f"[🔗 View Original]({post['url']})")
        
        # Origin tracing tab
        st.subheader("🌐 Origin Tracing")
        
        trace_content = st.text_area("Enter content to trace origin:", height=100)
        
        if st.button("🕵️ Trace Origin"):
            if trace_content:
                with st.spinner("Tracing origin..."):
                    components = load_components()
                    result = components['origin_tracer'].trace_rumor_origin(trace_content)
                    
                    st.write("**Origin Trace Results:**")
                    st.json(result)
    else:
        st.info("Enter a VIP name above and click 'Start VIP Content Scan' to begin analysis")
        
        with st.expander("ℹ️ How it works"):
            st.markdown('''
            **This tool searches for content about VIPs across:**
            - Twitter (via web scraping)
            - Reddit (via API)
            
            **Analysis includes:**
            - Misinformation risk scoring
            - Content pattern detection
            - Viral spread tracking
            - Origin tracing capabilities
            
            **No API limits - completely bypasses Twitter's restrictions!**
            ''')
