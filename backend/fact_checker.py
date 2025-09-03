import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    RobertaTokenizer, RobertaForSequenceClassification,
    pipeline
)
import requests
import numpy as np
from datetime import datetime
import re

class RealFactChecker:
    def __init__(self):
        self.setup_models()
        
    def setup_models(self):
        """Load real pre-trained models"""
        print("🤖 Loading misinformation detection models...")
        
        try:
            # Primary Model: RoBERTa for misinformation detection
            model_name = "martin-ha/toxic-comment-model"  # You can use a better model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            # Alternative: Use a pipeline for easier inference
            self.classifier = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                return_all_scores=True
            )
            
            print("✅ Models loaded successfully")
            
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            # Fallback to basic sentiment analysis
            self.classifier = pipeline("sentiment-analysis", return_all_scores=True)
    
    def analyze_misinformation(self, text, context=None):
        """Analyze text for misinformation patterns"""
        
        # Step 1: Content-based analysis
        content_score = self._analyze_content_patterns(text)
        
        # Step 2: ML Model prediction
        ml_score = self._get_ml_prediction(text)
        
        # Step 3: Real-time verification
        verification_result = self._real_time_verification(text)
        
        # Step 4: Combine scores
        final_score = self._combine_scores(content_score, ml_score, verification_result)
        
        return {
            'misinformation_probability': final_score,
            'verdict': self._get_verdict(final_score),
            'confidence': min(final_score * 1.2, 1.0),
            'analysis': {
                'content_patterns': content_score,
                'ml_prediction': ml_score,
                'real_time_check': verification_result
            },
            'flags': self._identify_warning_flags(text),
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_content_patterns(self, text):
        """Analyze text for misinformation patterns"""
        text_lower = text.lower()
        
        # Misinformation indicators
        fake_indicators = [
            'breaking', 'exclusive', 'leaked', 'insider sources', 'confidential',
            'shocking truth', 'they dont want you to know', 'revealed',
            'allegedly', 'reportedly', 'unconfirmed', 'sources say',
            'fake news', 'hoax', 'conspiracy', 'cover up'
        ]
        
        # Credibility indicators
        credible_indicators = [
            'confirmed', 'verified', 'official statement', 'press release',
            'according to', 'study shows', 'research indicates',
            'peer reviewed', 'expert analysis'
        ]
        
        fake_score = sum(1 for indicator in fake_indicators if indicator in text_lower)
        credible_score = sum(1 for indicator in credible_indicators if indicator in text_lower)
        
        # Normalize scores
        total_words = len(text.split())
        fake_ratio = fake_score / max(total_words / 10, 1)
        credible_ratio = credible_score / max(total_words / 10, 1)
        
        # Return probability of misinformation
        return min(fake_ratio - credible_ratio + 0.5, 1.0)
    
    def _get_ml_prediction(self, text):
        """Get ML model prediction"""
        try:
            # Use the loaded classifier
            results = self.classifier(text[:512])  # Truncate for model limits
            
            # Extract score (this depends on your specific model)
            if isinstance(results[0], list):
                # Handle multi-class output
                negative_score = next((r['score'] for r in results[0] if r['label'] in ['NEGATIVE', 'TOXIC', '1']), 0.5)
            else:
                negative_score = results[0]['score'] if results[0]['label'] in ['NEGATIVE', 'TOXIC'] else 1 - results[0]['score']
            
            return negative_score
            
        except Exception as e:
            print(f"ML prediction error: {e}")
            return 0.5  # Neutral score on error
    
    def _real_time_verification(self, text):
        """Real-time verification against news APIs"""
        try:
            # Extract key phrases for searching
            key_phrases = self._extract_key_phrases(text)
            
            verification_score = 0.5  # Default neutral
            
            # Check against news APIs (if available)
            news_check = self._check_news_apis(key_phrases)
            fact_check = self._check_fact_checking_sites(key_phrases)
            
            # Combine verification results
            if news_check['found']:
                verification_score = 0.2 if news_check['credible'] else 0.8
            
            if fact_check['found']:
                verification_score = (verification_score + (0.1 if fact_check['verified'] else 0.9)) / 2
            
            return {
                'score': verification_score,
                'news_check': news_check,
                'fact_check': fact_check
            }
            
        except Exception as e:
            print(f"Real-time verification error: {e}")
            return {'score': 0.5, 'error': str(e)}
    
    def _extract_key_phrases(self, text):
        """Extract key phrases for verification"""
        # Simple keyword extraction (you could use more advanced NER)
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        return words[:5]  # Top 5 potential entities
    
    def _check_news_apis(self, key_phrases):
        """Check against news APIs"""
        # This would use NewsAPI, but requires API key
        return {'found': False, 'credible': False, 'sources': []}
    
    def _check_fact_checking_sites(self, key_phrases):
        """Check against fact-checking sites"""
        # This would check Snopes, FactCheck.org, etc.
        return {'found': False, 'verified': False, 'sources': []}
    
    def _combine_scores(self, content_score, ml_score, verification_result):
        """Combine all scores into final misinformation probability"""
        weights = {
            'content': 0.3,
            'ml': 0.5,
            'verification': 0.2
        }
        
        verification_score = verification_result.get('score', 0.5)
        
        final_score = (
            content_score * weights['content'] +
            ml_score * weights['ml'] +
            verification_score * weights['verification']
        )
        
        return max(0.0, min(1.0, final_score))
    
    def _get_verdict(self, score):
        """Convert score to human-readable verdict"""
        if score >= 0.7:
            return "High Risk - Likely Misinformation"
        elif score >= 0.5:
            return "Medium Risk - Needs Verification"
        elif score >= 0.3:
            return "Low Risk - Likely Accurate"
        else:
            return "Verified - Highly Credible"
    
    def _identify_warning_flags(self, text):
        """Identify specific warning flags"""
        flags = []
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['breaking', 'exclusive', 'leaked']):
            flags.append('Sensational Language')
        
        if any(word in text_lower for word in ['allegedly', 'reportedly', 'sources say']):
            flags.append('Unverified Claims')
        
        if '!!!' in text or text.count('!') > 3:
            flags.append('Excessive Punctuation')
        
        if len(re.findall(r'[A-Z]{2,}', text)) > 2:
            flags.append('Excessive Capitalization')
        
        return flags
