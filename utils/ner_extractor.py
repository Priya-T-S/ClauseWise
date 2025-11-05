"""
Named Entity Recognition (NER) for Legal Documents
Extracts parties, dates, obligations, monetary values, and legal terms
"""

import re
from typing import Dict, List, Set
from datetime import datetime
from collections import defaultdict

class LegalNERExtractor:
    """Extract named entities from legal documents"""
    
    def __init__(self):
        self.entities = defaultdict(list)
        
        # Legal term patterns
        self.legal_terms = [
            'agreement', 'contract', 'covenant', 'warranty', 'indemnification',
            'liability', 'breach', 'termination', 'arbitration', 'jurisdiction',
            'confidentiality', 'non-disclosure', 'intellectual property',
            'consideration', 'force majeure', 'governing law', 'amendment',
            'severability', 'waiver', 'notice', 'assignment', 'subcontract'
        ]
        
        # Obligation keywords
        self.obligation_keywords = [
            'shall', 'must', 'will', 'agrees to', 'obligated to', 'required to',
            'responsible for', 'undertakes to', 'covenant to', 'bound to'
        ]
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict]]:
        """
        Extract all entities from legal text
        
        Args:
            text: Legal document text
            
        Returns:
            Dictionary of entity types and their instances
        """
        self.entities = defaultdict(list)
        
        # Extract different entity types
        self.entities['parties'] = self._extract_parties(text)
        self.entities['dates'] = self._extract_dates(text)
        self.entities['monetary_values'] = self._extract_monetary_values(text)
        self.entities['obligations'] = self._extract_obligations(text)
        self.entities['legal_terms'] = self._extract_legal_terms(text)
        self.entities['contact_info'] = self._extract_contact_info(text)
        
        return dict(self.entities)
    
    def _extract_parties(self, text: str) -> List[Dict]:
        """Extract party names from legal document"""
        parties = []
        
        # Pattern 1: "between X and Y"
        between_pattern = r'between\s+([A-Z][A-Za-z\s&,\.]+?)\s+(?:and|&)\s+([A-Z][A-Za-z\s&,\.]+?)(?:\s+|,|\.|\()'
        matches = re.finditer(between_pattern, text, re.IGNORECASE)
        for match in matches:
            party1 = match.group(1).strip()
            party2 = match.group(2).strip()
            if len(party1) < 50 and len(party2) < 50:  # Reasonable name length
                parties.append({
                    'name': party1,
                    'role': 'Party 1',
                    'context': match.group(0)
                })
                parties.append({
                    'name': party2,
                    'role': 'Party 2',
                    'context': match.group(0)
                })
        
        # Pattern 2: "hereinafter referred to as"
        referred_pattern = r'([A-Z][A-Za-z\s&,\.]+?)\s+[\("]?hereinafter\s+referred\s+to\s+as\s+["\']?([A-Z][A-Za-z\s]+?)["\']?[\)"]?'
        matches = re.finditer(referred_pattern, text, re.IGNORECASE)
        for match in matches:
            full_name = match.group(1).strip()
            short_name = match.group(2).strip()
            if len(full_name) < 100:
                parties.append({
                    'name': full_name,
                    'alias': short_name,
                    'role': 'Party',
                    'context': match.group(0)
                })
        
        # Pattern 3: Organizations (Inc., LLC, Ltd., Corp.)
        org_pattern = r'\b([A-Z][A-Za-z\s&]+?(?:Inc\.|LLC|Ltd\.|Corp\.|Corporation|Limited|Company))\b'
        matches = re.finditer(org_pattern, text)
        for match in matches:
            org_name = match.group(1).strip()
            if len(org_name) < 100 and org_name not in [p['name'] for p in parties]:
                parties.append({
                    'name': org_name,
                    'role': 'Organization',
                    'context': match.group(0)
                })
        
        return parties[:10]  # Limit to top 10 to avoid noise
    
    def _extract_dates(self, text: str) -> List[Dict]:
        """Extract dates from text"""
        dates = []
        
        # Pattern 1: Month DD, YYYY
        pattern1 = r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b'
        matches = re.finditer(pattern1, text, re.IGNORECASE)
        for match in matches:
            dates.append({
                'date': match.group(0),
                'format': 'Month DD, YYYY',
                'context': self._get_context(text, match.start(), match.end())
            })
        
        # Pattern 2: DD/MM/YYYY or MM/DD/YYYY
        pattern2 = r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b'
        matches = re.finditer(pattern2, text)
        for match in matches:
            dates.append({
                'date': match.group(0),
                'format': 'DD/MM/YYYY or MM/DD/YYYY',
                'context': self._get_context(text, match.start(), match.end())
            })
        
        # Pattern 3: YYYY-MM-DD
        pattern3 = r'\b(\d{4})-(\d{2})-(\d{2})\b'
        matches = re.finditer(pattern3, text)
        for match in matches:
            dates.append({
                'date': match.group(0),
                'format': 'YYYY-MM-DD',
                'context': self._get_context(text, match.start(), match.end())
            })
        
        return dates[:20]  # Limit to avoid excessive dates
    
    def _extract_monetary_values(self, text: str) -> List[Dict]:
        """Extract monetary amounts"""
        amounts = []
        
        # Pattern 1: $X,XXX.XX or $X.XX
        pattern1 = r'\$\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\b'
        matches = re.finditer(pattern1, text)
        for match in matches:
            amounts.append({
                'amount': match.group(0),
                'value': match.group(1).replace(',', ''),
                'currency': 'USD',
                'context': self._get_context(text, match.start(), match.end())
            })
        
        # Pattern 2: XXX dollars
        pattern2 = r'\b(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+(?:dollars?|USD)\b'
        matches = re.finditer(pattern2, text, re.IGNORECASE)
        for match in matches:
            amounts.append({
                'amount': match.group(0),
                'value': match.group(1).replace(',', ''),
                'currency': 'USD',
                'context': self._get_context(text, match.start(), match.end())
            })
        
        # Pattern 3: Other currencies (EUR, GBP, INR)
        pattern3 = r'\b(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+(EUR|GBP|INR|₹|€|£)\b'
        matches = re.finditer(pattern3, text, re.IGNORECASE)
        for match in matches:
            amounts.append({
                'amount': match.group(0),
                'value': match.group(1).replace(',', ''),
                'currency': match.group(2),
                'context': self._get_context(text, match.start(), match.end())
            })
        
        return amounts[:15]
    
    def _extract_obligations(self, text: str) -> List[Dict]:
        """Extract obligation clauses"""
        obligations = []
        
        # Split into sentences
        sentences = re.split(r'[.;]\s+', text)
        
        for sentence in sentences:
            # Check if sentence contains obligation keywords
            for keyword in self.obligation_keywords:
                if keyword.lower() in sentence.lower():
                    # Extract subject and obligation
                    obligations.append({
                        'clause': sentence.strip(),
                        'keyword': keyword,
                        'type': 'obligation'
                    })
                    break
        
        return obligations[:20]
    
    def _extract_legal_terms(self, text: str) -> List[Dict]:
        """Extract legal terminology"""
        terms = []
        text_lower = text.lower()
        
        for term in self.legal_terms:
            # Find all occurrences of the term
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = list(re.finditer(pattern, text_lower))
            
            if matches:
                # Get first occurrence with context
                match = matches[0]
                terms.append({
                    'term': term,
                    'count': len(matches),
                    'context': self._get_context(text, match.start(), match.end())
                })
        
        # Sort by frequency
        terms.sort(key=lambda x: x['count'], reverse=True)
        return terms[:15]
    
    def _extract_contact_info(self, text: str) -> List[Dict]:
        """Extract contact information"""
        contacts = []
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.finditer(email_pattern, text)
        for match in emails:
            contacts.append({
                'type': 'email',
                'value': match.group(0),
                'context': self._get_context(text, match.start(), match.end())
            })
        
        # Phone numbers (various formats)
        phone_pattern = r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'
        phones = re.finditer(phone_pattern, text)
        for match in phones:
            contacts.append({
                'type': 'phone',
                'value': match.group(0),
                'context': self._get_context(text, match.start(), match.end())
            })
        
        return contacts[:10]
    
    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get surrounding context for an entity"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        context = text[context_start:context_end].strip()
        
        # Add ellipsis if truncated
        if context_start > 0:
            context = '...' + context
        if context_end < len(text):
            context = context + '...'
        
        return context
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary of extracted entities"""
        return {
            'parties': len(self.entities.get('parties', [])),
            'dates': len(self.entities.get('dates', [])),
            'monetary_values': len(self.entities.get('monetary_values', [])),
            'obligations': len(self.entities.get('obligations', [])),
            'legal_terms': len(self.entities.get('legal_terms', [])),
            'contact_info': len(self.entities.get('contact_info', []))
        }