"""
Clause Analyzer for ClauseWise
Extracts and simplifies legal clauses using IBM Granite
"""

import re
from typing import List, Dict, Optional
from .granite_client import get_granite_client

class ClauseAnalyzer:
    """Analyze and simplify legal clauses"""
    
    def __init__(self):
        self.granite = get_granite_client()
        
        # Common clause types in legal documents
        self.clause_types = [
            'definitions', 'scope', 'term', 'termination', 'payment',
            'confidentiality', 'intellectual property', 'warranties',
            'liability', 'indemnification', 'force majeure', 'dispute resolution',
            'governing law', 'notices', 'amendments', 'severability'
        ]
    
    def extract_clauses(self, text: str) -> List[Dict]:
        """
        Extract individual clauses from legal document
        
        Args:
            text: Full legal document text
            
        Returns:
            List of extracted clauses with metadata
        """
        clauses = []
        
        # Strategy 1: Extract numbered/lettered clauses
        numbered_clauses = self._extract_numbered_clauses(text)
        if numbered_clauses:
            return numbered_clauses
        
        # Strategy 2: Extract by section headers
        section_clauses = self._extract_section_clauses(text)
        if section_clauses:
            return section_clauses
        
        # Strategy 3: Extract by sentence/paragraph if no structure found
        return self._extract_paragraph_clauses(text)
    
    def _extract_numbered_clauses(self, text: str) -> List[Dict]:
        """Extract clauses with numbering (1., 2., 1.1, etc.)"""
        clauses = []
        
        # Pattern for numbered clauses: 1., 2., etc. or 1.1, 1.2, etc.
        pattern = r'(?:^|\n)\s*(\d+\.(?:\d+\.)*)\s+([^\n]+(?:\n(?!\s*\d+\.)[^\n]+)*)'
        matches = re.finditer(pattern, text, re.MULTILINE)
        
        for match in matches:
            number = match.group(1).strip()
            content = match.group(2).strip()
            
            if len(content) > 20:  # Minimum clause length
                clause_type = self._identify_clause_type(content)
                clauses.append({
                    'number': number,
                    'content': content,
                    'type': clause_type,
                    'word_count': len(content.split())
                })
        
        return clauses
    
    def _extract_section_clauses(self, text: str) -> List[Dict]:
        """Extract clauses by section headers"""
        clauses = []
        
        # Pattern for section headers (e.g., "1. DEFINITIONS", "ARTICLE I - SCOPE")
        header_pattern = r'(?:^|\n)\s*(?:ARTICLE\s+[IVX\d]+|SECTION\s+\d+|\d+\.)\s*[-–—]?\s*([A-Z\s]+)(?:\n|\r)'
        
        matches = list(re.finditer(header_pattern, text, re.IGNORECASE))
        
        for i, match in enumerate(matches):
            title = match.group(1).strip()
            start = match.end()
            
            # Find end of section (next header or end of text)
            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(text)
            
            content = text[start:end].strip()
            
            if len(content) > 50:  # Minimum section length
                clauses.append({
                    'title': title,
                    'content': content,
                    'type': self._identify_clause_type(title + ' ' + content),
                    'word_count': len(content.split())
                })
        
        return clauses
    
    def _extract_paragraph_clauses(self, text: str) -> List[Dict]:
        """Extract clauses by paragraphs (fallback method)"""
        clauses = []
        
        # Split by double newlines or periods followed by newlines
        paragraphs = re.split(r'\n\s*\n|\.\s*\n', text)
        
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if len(para) > 100:  # Minimum paragraph length
                clause_type = self._identify_clause_type(para)
                clauses.append({
                    'number': f'P{i+1}',
                    'content': para,
                    'type': clause_type,
                    'word_count': len(para.split())
                })
        
        return clauses[:20]  # Limit to top 20 paragraphs
    
    def _identify_clause_type(self, text: str) -> str:
        """Identify the type of clause based on keywords"""
        text_lower = text.lower()
        
        # Check for clause type keywords
        for clause_type in self.clause_types:
            if clause_type.replace(' ', '') in text_lower.replace(' ', ''):
                return clause_type.title()
        
        # Check for common patterns
        if any(word in text_lower for word in ['define', 'definition', 'means']):
            return 'Definitions'
        elif any(word in text_lower for word in ['terminate', 'termination', 'cancel']):
            return 'Termination'
        elif any(word in text_lower for word in ['pay', 'payment', 'fee', 'compensation']):
            return 'Payment'
        elif any(word in text_lower for word in ['confidential', 'secret', 'proprietary']):
            return 'Confidentiality'
        elif any(word in text_lower for word in ['liable', 'liability', 'responsible']):
            return 'Liability'
        elif any(word in text_lower for word in ['warrant', 'guarantee', 'represent']):
            return 'Warranties'
        
        return 'General'
    
    def simplify_clause(self, clause_text: str, max_length: int = 500) -> Dict:
        """
        Simplify a legal clause using IBM Granite
        
        Args:
            clause_text: Original legal clause text
            max_length: Maximum length for simplified text
            
        Returns:
            Dictionary with original and simplified versions
        """
        system_prompt = """You are a legal document simplification expert. Your task is to rewrite complex legal clauses into simple, clear language that a layperson can understand. Follow these rules:

1. Use simple, everyday words instead of legal jargon
2. Break down complex sentences into shorter ones
3. Explain legal terms in plain language
4. Keep the core meaning and legal intent intact
5. Use active voice instead of passive voice
6. Be concise but complete
7. Format as clear bullet points if the clause has multiple parts"""

        user_prompt = f"""Simplify this legal clause into plain, easy-to-understand language:

ORIGINAL CLAUSE:
{clause_text}

SIMPLIFIED VERSION:"""

        try:
            simplified = self.granite.generate(user_prompt, system_prompt)
            
            # Clean up the response
            simplified = simplified.strip()
            
            # Truncate if too long
            if len(simplified) > max_length:
                simplified = simplified[:max_length] + "..."
            
            return {
                'original': clause_text,
                'simplified': simplified,
                'original_length': len(clause_text),
                'simplified_length': len(simplified),
                'reduction_percentage': round((1 - len(simplified) / len(clause_text)) * 100, 2)
            }
        except Exception as e:
            return {
                'original': clause_text,
                'simplified': f"Error simplifying clause: {str(e)}",
                'original_length': len(clause_text),
                'simplified_length': 0,
                'reduction_percentage': 0,
                'error': str(e)
            }
    
    def batch_simplify(self, clauses: List[Dict], max_clauses: int = 10) -> List[Dict]:
        """
        Simplify multiple clauses in batch
        
        Args:
            clauses: List of clause dictionaries
            max_clauses: Maximum number of clauses to simplify
            
        Returns:
            List of clauses with simplified versions
        """
        results = []
        
        # Limit to max_clauses to avoid long processing time
        for i, clause in enumerate(clauses[:max_clauses]):
            content = clause.get('content', '')
            
            # Skip very short clauses
            if len(content) < 50:
                continue
            
            result = self.simplify_clause(content)
            result['number'] = clause.get('number', clause.get('title', f'Clause {i+1}'))
            result['type'] = clause.get('type', 'General')
            results.append(result)
        
        return results
    
    def explain_legal_term(self, term: str) -> str:
        """Explain a legal term in simple language"""
        system_prompt = "You are a legal terminology expert. Explain legal terms in simple, clear language that anyone can understand."
        
        user_prompt = f"Explain what '{term}' means in legal contexts, using simple language:"
        
        try:
            explanation = self.granite.generate(user_prompt, system_prompt)
            return explanation.strip()
        except Exception as e:
            return f"Error explaining term: {str(e)}"
    
    def get_clause_summary(self, clauses: List[Dict]) -> Dict:
        """Get summary statistics for extracted clauses"""
        if not clauses:
            return {
                'total_clauses': 0,
                'total_words': 0,
                'avg_words_per_clause': 0,
                'clause_types': {}
            }
        
        total_words = sum(c.get('word_count', 0) for c in clauses)
        clause_types = {}
        
        for clause in clauses:
            clause_type = clause.get('type', 'General')
            clause_types[clause_type] = clause_types.get(clause_type, 0) + 1
        
        return {
            'total_clauses': len(clauses),
            'total_words': total_words,
            'avg_words_per_clause': round(total_words / len(clauses), 2),
            'clause_types': clause_types
        }