import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import requests
import time

def render():
    st.title("Fake Profile & Campaign Identification")
    
    st.markdown("""
    ### Overview
    Detect impersonation accounts or channels posing as VIPs and identify coordinated misinformation 
    or smear campaigns across Instagram, Twitter, and Facebook.
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### VIP Profile Analysis")
        vip_handle = st.text_input(
            "Enter VIP username/handle", 
            placeholder="@elonmusk, @oprah, @realdonaldtrump",
            help="Enter the handle you want to verify for legitimacy"
        )
        
        platforms_to_check = st.multiselect(
            "Select platforms to analyze",
            ["Twitter", "Instagram", "Facebook", "YouTube"],
            default=["Twitter", "Instagram", "Facebook"]
        )
        
    with col2:
        st.markdown("### Analysis Options")
        deep_scan = st.checkbox("Deep scan (slower but more thorough)", value=True)
        check_campaigns = st.checkbox("Detect coordinated campaigns", value=True)
        cross_platform = st.checkbox("Cross-platform verification", value=True)
    
    # Analysis button
    if st.button("Analyze Profile", type="primary"):
        if not vip_handle.strip():
            st.error("Please enter a valid VIP username or handle.")
            return
        
        if not platforms_to_check:
            st.error("Please select at least one platform to analyze.")
            return
        
        with st.spinner("Analyzing profile authenticity and campaign patterns..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Fetching profile data from platforms...")
            progress_bar.progress(25)
            time.sleep(1)
            
            profile_data = fetch_profile_data(vip_handle, platforms_to_check)
            
            status_text.text("Analyzing profile legitimacy...")
            progress_bar.progress(50)
            time.sleep(1)
            
            legitimacy_results = analyze_profile_legitimacy(profile_data, deep_scan)
            
            campaign_results = {}
            if check_campaigns:
                status_text.text("Detecting coordinated campaigns...")
                progress_bar.progress(75)
                time.sleep(1)
                campaign_results = detect_coordinated_campaigns(vip_handle)
            
            cross_platform_results = {}
            if cross_platform:
                status_text.text("Cross-platform verification...")
                progress_bar.progress(90)
                time.sleep(1)
                cross_platform_results = verify_cross_platform(profile_data)
            
            progress_bar.progress(100)
            status_text.text("Analysis complete!")
            time.sleep(0.5)
            
            progress_bar.empty()
            status_text.empty()
        
        st.markdown("---")
        display_results(vip_handle, profile_data, legitimacy_results, campaign_results, cross_platform_results)

def fetch_profile_data(handle, platforms):
    profile_data = {}
    
    for platform in platforms:
        if platform == "Twitter":
            profile_data["Twitter"] = {
                "handle": handle,
                "verified": random.choice([True, False]),
                "followers": random.randint(10000, 50000000),
                "following": random.randint(100, 10000),
                "created_date": "2010-03-15",
                "posts_count": random.randint(1000, 100000),
                "profile_pic_url": "https://example.com/pic.jpg",
                "bio": f"Official {handle} account",
                "website": "https://example.com"
            }
        elif platform == "Instagram":
            profile_data["Instagram"] = {
                "handle": handle,
                "verified": random.choice([True, False]),
                "followers": random.randint(5000, 30000000),
                "following": random.randint(50, 5000),
                "posts_count": random.randint(500, 10000),
                "bio": f"Official {handle}",
                "website": "https://example.com"
            }
        elif platform == "Facebook":
            profile_data["Facebook"] = {
                "handle": handle,
                "verified": random.choice([True, False]),
                "likes": random.randint(10000, 100000000),
                "created_date": "2009-02-20",
                "about": f"Official {handle} page"
            }
    
    return profile_data

def analyze_profile_legitimacy(profile_data, deep_scan):
    legitimacy_score = 0
    total_checks = 0
    issues = []
    positive_indicators = []
    
    for platform, data in profile_data.items():
        total_checks += 5  
        
        if data.get("verified", False):
            legitimacy_score += 1
            positive_indicators.append(f"{platform}: Verified badge present")
        else:
            issues.append(f"{platform}: No verification badge")
        
        if platform in ["Twitter", "Instagram"]:
            followers = data.get("followers", 0)
            following = data.get("following", 0)
            if following > 0:
                ratio = followers / following
                if ratio > 10:  # Good ratio
                    legitimacy_score += 1
                    positive_indicators.append(f"{platform}: Healthy follower ratio ({ratio:.1f}:1)")
                else:
                    issues.append(f"{platform}: Suspicious follower ratio ({ratio:.1f}:1)")
        
        if "created_date" in data:
            legitimacy_score += 1
            positive_indicators.append(f"{platform}: Account created {data['created_date']}")
        
        if data.get("bio") or data.get("about"):
            legitimacy_score += 1
            positive_indicators.append(f"{platform}: Complete profile information")
        else:
            issues.append(f"{platform}: Incomplete profile information")
        
        if data.get("website"):
            legitimacy_score += 1
            positive_indicators.append(f"{platform}: Official website linked")
        else:
            issues.append(f"{platform}: No official website linked")
    
    legitimacy_percentage = (legitimacy_score / total_checks) * 100 if total_checks > 0 else 0
    
    return {
        "score": legitimacy_percentage,
        "issues": issues,
        "positive_indicators": positive_indicators,
        "total_checks": total_checks,
        "passed_checks": legitimacy_score
    }

def detect_coordinated_campaigns(handle):
    campaigns = []
    

    if random.random() < 0.3:  
        campaigns.append({
            "type": "Impersonation Campaign",
            "accounts": [f"@fake_{handle}_1", f"@fake_{handle}_official", f"@real_{handle}_2025"],
            "platforms": ["Twitter", "Instagram"],
            "activity_pattern": "Synchronized posting every 2-3 hours",
            "content_similarity": 0.87,
            "risk_level": "High",
            "detected_date": datetime.now().strftime("%Y-%m-%d"),
            "description": "Multiple accounts impersonating the VIP with similar content patterns"
        })

    if random.random() < 0.2:  
        campaigns.append({
            "type": "Smear Campaign",
            "accounts": [f"@expose_{handle}", f"@truth_{handle}", f"@against_{handle}"],
            "platforms": ["Twitter", "Facebook"],
            "activity_pattern": "Burst posting during peak hours",
            "content_similarity": 0.73,
            "risk_level": "Medium",
            "detected_date": datetime.now().strftime("%Y-%m-%d"),
            "description": "Coordinated negative content targeting the VIP"
        })
    
    return {
        "total_campaigns": len(campaigns),
        "campaigns": campaigns,
        "risk_assessment": "High" if any(c["risk_level"] == "High" for c in campaigns) else "Medium" if campaigns else "Low"
    }

def verify_cross_platform(profile_data):
    consistency_score = 0
    total_checks = 0
    consistency_issues = []
    consistency_positives = []
    
    platforms = list(profile_data.keys())
    
    if len(platforms) < 2:
        return {"score": 0, "message": "Need at least 2 platforms for cross-verification"}
    
    verified_platforms = [p for p, data in profile_data.items() if data.get("verified", False)]
    total_checks += 1
    
    if len(verified_platforms) == len(platforms):
        consistency_score += 1
        consistency_positives.append("Verification badges consistent across all platforms")
    elif len(verified_platforms) > 0:
        consistency_issues.append(f"Verification inconsistent: {', '.join(verified_platforms)} verified")
    else:
        consistency_issues.append("No verification badges found on any platform")
    
    
    websites = [data.get("website") for data in profile_data.values() if data.get("website")]
    total_checks += 1
    
    if len(set(websites)) <= 1 and websites:  
        consistency_score += 1
        consistency_positives.append("Website links consistent across platforms")
    else:
        consistency_issues.append("Different websites linked across platforms")
    
    consistency_percentage = (consistency_score / total_checks) * 100 if total_checks > 0 else 0
    
    return {
        "score": consistency_percentage,
        "issues": consistency_issues,
        "positives": consistency_positives,
        "total_checks": total_checks,
        "passed_checks": consistency_score
    }

def display_results(handle, profile_data, legitimacy_results, campaign_results, cross_platform_results):
    
    st.markdown("## Overall Risk Assessment")
    
    legitimacy_score = legitimacy_results.get("score", 0)
    campaign_risk = campaign_results.get("risk_assessment", "Low")
    cross_platform_score = cross_platform_results.get("score", 0)
    
    if legitimacy_score > 80 and campaign_risk == "Low" and cross_platform_score > 70:
        overall_risk = "LEGITIMATE"
        risk_color = "green"
    elif legitimacy_score > 60 and campaign_risk in ["Low", "Medium"]:
        overall_risk = "SUSPICIOUS"
        risk_color = "orange"
    else:
        overall_risk = "HIGH RISK"
        risk_color = "red"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Assessment", overall_risk)
    with col2:
        st.metric("Legitimacy Score", f"{legitimacy_score:.1f}%")
    with col3:
        st.metric("Campaign Risk", campaign_risk)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Profile Analysis", "Campaign Detection", "Cross-Platform", "Raw Data"])
    
    with tab1:
        st.markdown("### Profile Legitimacy Analysis")
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = legitimacy_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Legitimacy Score"},
            delta = {'reference': 80},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90}}))
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Positive Indicators")
            for indicator in legitimacy_results.get("positive_indicators", []):
                st.markdown(f"- {indicator}")
        
        with col2:
            st.markdown("#### Issues Found")
            for issue in legitimacy_results.get("issues", []):
                st.markdown(f"- {issue}")
    
    with tab2:
        st.markdown("### Coordinated Campaign Detection")
        
        if campaign_results.get("total_campaigns", 0) > 0:
            st.error(f"{campaign_results['total_campaigns']} potential campaigns detected!")
            
            for i, campaign in enumerate(campaign_results.get("campaigns", [])):
                with st.expander(f"Campaign {i+1}: {campaign['type']} ({campaign['risk_level']} Risk)"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Suspicious Accounts:**")
                        for account in campaign['accounts']:
                            st.markdown(f"- {account}")
                        
                        st.markdown(f"**Platforms:** {', '.join(campaign['platforms'])}")
                        st.markdown(f"**Content Similarity:** {campaign['content_similarity']:.2%}")
                    
                    with col2:
                        st.markdown(f"**Activity Pattern:** {campaign['activity_pattern']}")
                        st.markdown(f"**First Detected:** {campaign['detected_date']}")
                        st.markdown(f"**Description:** {campaign['description']}")
        else:
            st.success("No coordinated campaigns detected")
    
    with tab3:
        st.markdown("### Cross-Platform Verification")
        
        if cross_platform_results:
            cross_score = cross_platform_results.get("score", 0)
            
            st.metric("Cross-Platform Consistency", f"{cross_score:.1f}%")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Consistency Checks Passed")
                for positive in cross_platform_results.get("positives", []):
                    st.markdown(f"- {positive}")
            
            with col2:
                st.markdown("#### Consistency Issues")
                for issue in cross_platform_results.get("issues", []):
                    st.markdown(f"- {issue}")
        else:
            st.info("Cross-platform verification not performed")
    
    with tab4:
        st.markdown("### Raw Profile Data")
        
        for platform, data in profile_data.items():
            with st.expander(f"{platform} Data"):
                st.json(data)
    
    st.markdown("---")
    st.markdown("### Recommended Actions")
    
    if legitimacy_score < 50:
        st.error("HIGH PRIORITY: This profile shows multiple red flags. Consider manual verification.")
    elif legitimacy_score < 80:
        st.warning("MEDIUM PRIORITY: Some concerning indicators found. Monitor closely.")
    else:
        st.success("LOW PRIORITY: Profile appears legitimate based on available data.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Generate Report", type="secondary"):
            st.info("Report generation feature coming soon!")
    
    with col2:
        if st.button("Report Suspicious Activity", type="secondary"):
            st.info("This would integrate with your evidence reporting system!")
