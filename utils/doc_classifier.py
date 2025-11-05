"""
Document Type Classifier for ClauseWise
Classifies legal documents into categories using IBM Granite
"""

from typing import Dict, List, Tuple
import re
from .granite_client import get_granite_client

class DocumentClassifier:
    """Classify legal document types"""
    
    def __init__(self):
        self.granite = get_granite_client()
        
        # Document type signatures (keywords and patterns)
        self.document_signatures = {
            'Non-Disclosure Agreement (NDA)': {
                'keywords': ['confidential', 'non-disclosure', 'proprietary information', 
                           'trade secret', 'confidentiality', 'receiving party', 'disclosing party'],
                'patterns': [r'non[-\s]disclosure', r'NDA', r'confidentiality\s+agreement'],
                'weight': 1.0
            },
            'Employment Contract': {
                'keywords': ['employee', 'employer', 'employment', 'salary', 'compensation',
                           'job title', 'duties', 'responsibilities', 'benefits', 'vacation',
                           'termination of employment', 'at-will'],
                'patterns': [r'employment\s+agreement', r'offer\s+letter', r'employee\s+handbook'],
                'weight': 1.0
            },
            'Lease Agreement': {
                'keywords': ['lease', 'tenant', 'landlord', 'rent', 'premises', 'property',
                           'security deposit', 'maintenance', 'lease term', 'rental'],
                'patterns': [r'lease\s+agreement', r'rental\s+agreement', r'tenancy'],
                'weight': 1.0
            },
            'Service Agreement': {
                'keywords': ['services', 'service provider', 'client', 'deliverables',
                           'scope of work', 'professional services', 'consulting',
                           'independent contractor', 'statement of work'],
                'patterns': [r'service\s+agreement', r'consulting\s+agreement', 
                           r'professional\s+services', r'statement\s+of\s+work', r'SOW'],
                'weight': 1.0
            },
            'Purchase Agreement': {
                'keywords': ['purchase', 'buyer', 'seller', 'goods', 'merchandise',
                           'delivery', 'shipping', 'purchase price', 'payment terms'],
                'patterns': [r'purchase\s+agreement', r'sales\s+agreement', 
                           r'purchase\s+order', r'bill\s+of\s+sale'],
                'weight': 1.0
            },
            'Partnership Agreement': {
                'keywords': ['partner', 'partnership', 'capital contribution', 'profit sharing',
                           'loss sharing', 'management', 'dissolution', 'partnership interest'],
                'patterns': [r'partnership\s+agreement', r'joint\s+venture'],
                'weight': 1.0
            },
            'License Agreement': {
                'keywords': ['license', 'licensor', 'licensee', 'intellectual property',
                           'usage rights', 'royalty', 'sublicense', 'license fee'],
                'patterns': [r'license\s+agreement', r'licensing\s+agreement', r'software\s+license'],
                'weight': 1.0
            },
            'Loan Agreement': {
                'keywords': ['loan', 'lender', 'borrower', 'principal', 'interest rate',
                           'repayment', 'default', 'collateral', 'promissory note'],
                'patterns': [r'loan\s+agreement', r'promissory\s+note', r'credit\s+agreement'],
                'weight': 1.0
            },
            'Settlement Agreement': {
                'keywords': ['settlement', 'dispute', 'claim', 'release', 'parties agree',
                           'consideration', 'waiver', 'mutual release'],
                'patterns': [r'settlement\s+agreement', r'release\s+agreement', r'compromise'],
                'weight': 1.0
            },
            'Franchise Agreement': {
                'keywords': ['franchise', 'franchisor', 'franchisee', 'territory',
                           'operating system', 'franchise fee', 'royalty'],
                'patterns': [r'franchise\s+agreement', r'franchising'],
                'weight': 1.0
            }
        }
    
    def classify_document(self, text: str, use_ai: bool = True) -> Dict:
        """
        Classify legal document type
        
        Args:
            text: Document text
            use_ai: Whether to use AI for classification (True) or rule-based only (False)
            
        Returns:
            Dictionary with classification results
        """
        # Rule-based classification
        rule_scores = self._rule_based_classification(text)
        
        # Get top 3 candidates from rule-based
        top_candidates = sorted(rule_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        if use_ai and top_candidates[0][1] < 5:  # Use AI if confidence is low
            # AI-based classification using Granite
            ai_classification = self._ai_classification(text, [c[0] for c in top_candidates])
            
            return {
                'document_type': ai_classification['type'],
                'confidence': ai_classification['confidence'],
                'method': 'AI-enhanced',
                'rule_based_scores': dict(top_candidates),
                'reasoning': ai_classification.get('reasoning', '')
            }
        else:
            # Use rule-based result
            doc_type = top_candidates[0][0]
            score = top_candidates[0][1]
            confidence = min(score / 10 * 100, 100)  # Convert to percentage
            
            return {
                'document_type': doc_type,
                'confidence': round(confidence, 2),
                'method': 'Rule-based',
                'rule_based_scores': dict(top_candidates),
                'reasoning': f'Identified based on keyword and pattern matching'
            }
    
    def _rule_based_classification(self, text: str) -> Dict[str, float]:
        """Rule-based classification using keywords and patterns"""
        text_lower = text.lower()
        scores = {}
        
        for doc_type, signature in self.document_signatures.items():
            score = 0.0
            
            # Score based on keywords
            for keyword in signature['keywords']:
                if keyword.lower() in text_lower:
                    score += 1.0
            
            # Score based on patterns (weighted higher)
            for pattern in signature['patterns']:
                matches = len(re.findall(pattern, text_lower))
                score += matches * 2.0
            
            scores[doc_type] = score
        
        return scores
    
    def _ai_classification(self, text: str, candidates: List[str]) -> Dict:
        """AI-based classification using IBM Granite"""
        # Truncate text if too long
        max_text_length = 2000
        if len(text) > max_text_length:
            text = text[:max_text_length] + "..."
        
        system_prompt = """You are a legal document classification expert. Your task is to accurately identify the type of legal document based on its content."""
        
        candidates_str = ", ".join(candidates) if candidates else "NDA, Employment Contract, Lease Agreement, Service Agreement"
        
        user_prompt = f"""Analyze this legal document and classify it into one of these categories: {candidates_str}

Document text:
{text}

Provide your answer in this format:
Document Type: [type]
Confidence: [High/Medium/Low]
Reasoning: [brief explanation]"""

        try:
            response = self.granite.generate(user_prompt, system_prompt)
            
            # Parse response
            doc_type = None
            confidence = 'Medium'
            reasoning = ''
            
            for line in response.split('\n'):
                if 'document type:' in line.lower():
                    doc_type = line.split(':', 1)[1].strip()
                elif 'confidence:' in line.lower():
                    confidence = line.split(':', 1)[1].strip()
                elif 'reasoning:' in line.lower():
                    reasoning = line.split(':', 1)[1].strip()
            
            # Convert confidence to percentage
            confidence_map = {'high': 90, 'medium': 70, 'low': 50}
            confidence_score = confidence_map.get(confidence.lower(), 70)
            
            # Validate doc_type
            if not doc_type or doc_type not in self.document_signatures:
                # Try to find closest match
                for known_type in self.document_signatures.keys():
                    if known_type.lower() in (doc_type or '').lower():
                        doc_type = known_type
                        break
                else:
                    doc_type = candidates[0] if candidates else 'Unknown'
            
            return {
                'type': doc_type,
                'confidence': confidence_score,
                'reasoning': reasoning
            }
        except Exception as e:
            return {
                'type': candidates[0] if candidates else 'Unknown',
                'confidence': 50,
                'reasoning': f'Error in AI classification: {str(e)}'
            }
    
    def get_document_characteristics(self, text: str) -> Dict:
        """Extract characteristics that help identify document type"""
        characteristics = {
            'has_parties': False,
            'has_monetary_terms': False,
            'has_dates': False,
            'has_signatures': False,
            'has_legal_jargon': False,
            'estimated_formality': 'Medium'
        }
        
        text_lower = text.lower()
        
        # Check for parties
        if any(term in text_lower for term in ['between', 'party', 'parties', 'hereinafter']):
            characteristics['has_parties'] = True
        
        # Check for monetary terms
        if re.search(r'\$|\d+(?:,\d{3})*(?:\.\d{2})?', text) or 'payment' in text_lower:
            characteristics['has_monetary_terms'] = True
        
        # Check for dates
        if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|january|february|march|april|may|june|july|august|september|october|november|december', text_lower):
            characteristics['has_dates'] = True
        
        # Check for signature lines
        if any(term in text_lower for term in ['signature', 'signed', 'executed', 'witness']):
            characteristics['has_signatures'] = True
        
        # Check for legal jargon
        legal_terms = ['whereas', 'hereby', 'hereinafter', 'notwithstanding', 'pursuant']
        jargon_count = sum(1 for term in legal_terms if term in text_lower)
        characteristics['has_legal_jargon'] = jargon_count >= 2
        
        # Estimate formality
        if jargon_count >= 4:
            characteristics['estimated_formality'] = 'High'
        elif jargon_count <= 1:
            characteristics['estimated_formality'] = 'Low'
        
        return characteristics
    
    def suggest_similar_documents(self, doc_type: str) -> List[str]:
        """Suggest similar document types"""
        similarity_map = {
            'Non-Disclosure Agreement (NDA)': ['Service Agreement', 'Employment Contract'],
            'Employment Contract': ['Service Agreement', 'Non-Disclosure Agreement (NDA)'],
            'Lease Agreement': ['Purchase Agreement', 'Service Agreement'],
            'Service Agreement': ['Employment Contract', 'Non-Disclosure Agreement (NDA)'],
            'Purchase Agreement': ['Lease Agreement', 'Loan Agreement'],
            'Partnership Agreement': ['Service Agreement', 'License Agreement'],
            'License Agreement': ['Service Agreement', 'Partnership Agreement'],
            'Loan Agreement': ['Purchase Agreement', 'Settlement Agreement'],
            'Settlement Agreement': ['Loan Agreement', 'Service Agreement'],
            'Franchise Agreement': ['Partnership Agreement', 'License Agreement']
        }
        
        return similarity_map.get(doc_type, [])