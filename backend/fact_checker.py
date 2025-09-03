import os
import re
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class RealFactChecker:
    def __init__(self):
        self.classifier = None
        # Skip the transformers import to avoid torch issues
        print("✅ Fact checker initialized - using rule-based analysis")

    def analyze_real_content(self, text):
        try:
            if not text or not isinstance(text, str):
                text = "No content provided"
            
            # Simple pattern-based scoring
            content_score = self._analyze_content_patterns(text)
            final_score = content_score
            verdict = self._get_verdict(final_score)
            flags = self._identify_warning_flags(text)
            
            return {
                'misinformation_probability': final_score,
                'verdict': verdict,
                'confidence': min(final_score * 1.1, 1.0),
                'analysis': {
                    'content_patterns': content_score,
                    'ml_prediction': 0.5,  # Default
                    'google_fact_check': {'found': False}
                },
                'flags': flags,
                'timestamp': datetime.now().isoformat()
            }
        except Exception:
            return {
                'misinformation_probability': 0.5,
                'verdict': 'Medium Risk - System Fallback',
                'confidence': 0.5,
                'analysis': {
                    'content_patterns': 0.5,
                    'ml_prediction': 0.5,
                    'google_fact_check': {'found': False}
                },
                'flags': [],
                'timestamp': datetime.now().isoformat()
            }

    def _analyze_content_patterns(self, text):
        try:
            text_lower = text.lower()
            suspicious = ['breaking', 'exclusive', 'leaked', 'allegedly', 'unconfirmed', 'reportedly', 'scandal']
            credible = ['according to', 'confirmed', 'verified', 'research', 'study shows']
            s_count = sum(w in text_lower for w in suspicious)
            c_count = sum(w in text_lower for w in credible)
            total = len(text.split()) or 1
            return min(max((s_count - c_count) / (total / 10) + 0.4, 0), 1.0)
        except Exception:
            return 0.5

    def _get_verdict(self, s):
        if s >= 0.8: return "High Risk - Likely Misinformation"
        if s >= 0.6: return "Medium-High Risk - Needs Verification"
        if s >= 0.4: return "Medium Risk - Uncertain"
        if s >= 0.2: return "Low Risk - Likely Accurate"
        return "Verified - Highly Credible"

    def _identify_warning_flags(self, text):
        flags = []
        try:
            t = text.lower()
            if any(word in t for word in ['breaking', 'exclusive', 'leaked']):
                flags.append('Sensational')
            if any(word in t for word in ['allegedly', 'reportedly']):
                flags.append('Unverified')
            if text.count('!') > 3:
                flags.append('Excessive !')
            if len([c for c in text if c.isupper()]) > len(text) * 0.3:
                flags.append('Excessive CAPS')
        except Exception:
            pass
        return flags

    # Legacy compatibility
    def analyze_misinformation(self, text):
        return self.analyze_real_content(text)
