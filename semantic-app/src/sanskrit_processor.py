"""
Sanskrit Text Processing System for Rig Veda Analysis
Based on Rick Briggs' 1985 research and ancient Indian grammatical tradition

This system processes actual Sanskrit text using the karaka framework
identified by Briggs as equivalent to modern semantic nets.
"""

import unicodedata
from typing import Dict, List, Tuple, Set, Optional
import re
from dataclasses import dataclass
from collections import defaultdict

# Sanskrit karaka (case) relations from Paninian grammar
KARAKA_RELATIONS = {
    'karta': 'agent',        # Who does the action (nominative)
    'karma': 'object',       # What receives the action (accusative) 
    'karana': 'instrument',  # By what means (instrumental)
    'sampradana': 'recipient', # To whom given (dative)
    'apadana': 'source',     # From what separated (ablative)
    'adhikarana': 'location', # Where/when (locative)
    'sambandha': 'possessor'  # Whose (genitive)
}

@dataclass
class SanskritTriple:
    """Sanskrit semantic triple with karaka relations"""
    verb_root: str           # Sanskrit dhatu (verb root)
    karaka: str             # Karaka relation (karta, karma, etc.)
    word: str               # Sanskrit word in context
    devanagari: str = ""    # Original Devanagari text
    meaning: str = ""       # English meaning
    
    def __str__(self):
        return f"{self.verb_root}, {self.karaka}, {self.word}"

class SanskritProcessor:
    """
    Processes Sanskrit text using traditional grammatical analysis
    following the Paninian tradition that Briggs identified.
    """
    
    def __init__(self):
        self.triples: List[SanskritTriple] = []
        self.vocabulary: Dict[str, str] = {}
        self.verb_roots: Set[str] = set()
        
        # Initialize with some basic Rig Vedic vocabulary
        self._initialize_vedic_vocabulary()
    
    def _initialize_vedic_vocabulary(self):
        """Initialize with common Rig Vedic words and roots"""
        # Common verb roots from Rig Veda
        self.verb_roots.update([
            'gam', 'as', 'bhu', 'kr', 'da', 'yaj', 'stu', 'gai', 'vac', 'ji'
        ])
        
        # Basic vocabulary (romanized Sanskrit)
        self.vocabulary.update({
            # Deities
            'agni': 'fire/fire-god',
            'indra': 'Indra (king of gods)',
            'soma': 'soma (sacred drink)',
            'surya': 'sun/sun-god',
            'vayu': 'wind/wind-god',
            'varuna': 'Varuna (god of waters)',
            
            # Common words
            'deva': 'god/divine',
            'mantra': 'sacred formula',
            'yaja': 'sacrifice', 
            'havya': 'oblation',
            'stoma': 'praise/hymn',
            'rta': 'cosmic order',
            
            # Pronouns and common particles
            'tvam': 'you',
            'aham': 'I',
            'sa': 'he/that',
            'ya': 'who/which',
            'ca': 'and',
            'va': 'or'
        })
    
    def normalize_sanskrit(self, text: str) -> str:
        """Normalize Sanskrit text (handle different input formats)"""
        # Handle various romanization schemes
        text = text.lower().strip()
        
        # Common romanization normalizations
        replacements = {
            'ṛ': 'r',   # Vocalic r
            'ṝ': 'rr',  # Long vocalic r  
            'ḷ': 'l',   # Vocalic l
            'ṁ': 'm',   # Anusvara variants
            'ṃ': 'm',
            'ḥ': 'h',   # Visarga
            'ś': 's',   # Palatals
            'ṣ': 's',   # Retroflexes
            'ṭ': 't',
            'ḍ': 'd',
            'ṇ': 'n',
            'ñ': 'n'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def tokenize_sanskrit(self, text: str) -> List[str]:
        """Basic Sanskrit tokenization"""
        text = self.normalize_sanskrit(text)
        
        # Split on whitespace and common punctuation
        tokens = re.findall(r'\b\w+\b', text)
        return [token for token in tokens if token]
    
    def analyze_sentence(self, sanskrit_text: str, translation: str = "") -> List[SanskritTriple]:
        """
        Analyze Sanskrit sentence using karaka framework
        This is a basic implementation - we'll enhance with ML later
        """
        tokens = self.tokenize_sanskrit(sanskrit_text)
        triples = []
        
        # Look for verb patterns and apply karaka analysis
        for i, token in enumerate(tokens):
            # Try to identify verb roots
            for root in self.verb_roots:
                if root in token or token.startswith(root):
                    # Found potential verb, analyze surrounding context
                    verb_triples = self._analyze_verb_context(root, tokens, i)
                    triples.extend(verb_triples)
                    break
        
        return triples
    
    def _analyze_verb_context(self, verb_root: str, tokens: List[str], verb_pos: int) -> List[SanskritTriple]:
        """Analyze context around a verb to extract karaka relations"""
        triples = []
        
        # Simple heuristic analysis (to be enhanced with proper morphological analysis)
        for i, token in enumerate(tokens):
            if i == verb_pos:
                continue
                
            # Basic karaka assignment based on position and ending patterns
            karaka = self._guess_karaka(token, i, verb_pos, tokens)
            if karaka:
                meaning = self.vocabulary.get(token, "unknown")
                triple = SanskritTriple(
                    verb_root=verb_root,
                    karaka=karaka,
                    word=token,
                    meaning=meaning
                )
                triples.append(triple)
                self.triples.append(triple)
        
        return triples
    
    def _guess_karaka(self, token: str, pos: int, verb_pos: int, tokens: List[str]) -> Optional[str]:
        """
        Guess karaka relation based on morphological clues
        This is simplified - proper analysis needs full morphological parsing
        """
        # Check common case endings (very basic)
        if token.endswith('a') or token.endswith('ah'):
            return 'karta'  # Likely nominative (agent)
        elif token.endswith('am'):
            return 'karma'  # Likely accusative (object)
        elif token.endswith('ena') or token.endswith('a'):
            return 'karana'  # Likely instrumental
        elif token.endswith('e') or token.endswith('ya'):
            return 'sampradana'  # Likely dative
        elif token.endswith('at') or token.endswith('ad'):
            return 'apadana'  # Likely ablative
        elif token.endswith('e') or token.endswith('su'):
            return 'adhikarana'  # Likely locative
        else:
            # Default assignment based on position
            if pos < verb_pos:
                return 'karta'  # Before verb, likely agent
            else:
                return 'karma'  # After verb, likely object
    
    def process_rigveda_verse(self, verse_text: str, translation: str = "") -> Dict:
        """Process a complete Rig Veda verse"""
        # Split into padas (quarters) if needed
        lines = verse_text.strip().split('\n')
        
        analysis = {
            'original': verse_text,
            'translation': translation,
            'triples': [],
            'vocabulary_used': set(),
            'verb_roots_found': set()
        }
        
        for line in lines:
            if line.strip():
                line_triples = self.analyze_sentence(line.strip())
                analysis['triples'].extend(line_triples)
                
                # Track vocabulary and roots
                for triple in line_triples:
                    analysis['vocabulary_used'].add(triple.word)
                    analysis['verb_roots_found'].add(triple.verb_root)
        
        return analysis
    
    def visualize_analysis(self, analysis: Dict) -> str:
        """Create visualization of Sanskrit analysis"""
        output = "🕉️ RIG VEDA ANALYSIS 🕉️\n"
        output += "=" * 50 + "\n\n"
        
        output += f"�� Original Sanskrit:\n{analysis['original']}\n\n"
        
        if analysis['translation']:
            output += f"🌍 Translation:\n{analysis['translation']}\n\n"
        
        output += f"🔗 Karaka Analysis ({len(analysis['triples'])} relations):\n"
        for i, triple in enumerate(analysis['triples'], 1):
            karaka_eng = KARAKA_RELATIONS.get(triple.karaka, triple.karaka)
            output += f"  {i:2d}. {triple.verb_root} → {karaka_eng} → {triple.word}"
            if triple.meaning:
                output += f" ({triple.meaning})"
            output += "\n"
        
        output += f"\n📚 Vocabulary: {', '.join(sorted(analysis['vocabulary_used']))}\n"
        output += f"🌱 Verb Roots: {', '.join(sorted(analysis['verb_roots_found']))}\n"
        
        return output

# Example usage with actual Rig Veda content
if __name__ == "__main__":
    processor = SanskritProcessor()
    
    print("🕉️ SANSKRIT RIG VEDA PROCESSOR 🕉️")
    print("Based on Rick Briggs' 1985 Research")
    print("=" * 60)
    
    # Example: RV 1.1.1 (first verse of Rig Veda)
    rigveda_verse = """
    agnim ide purohitam
    yajnasya devam rtvijam
    hotaram ratnadhatamam
    """
    
    translation = """
    I praise Agni, the priest,
    the divine minister of sacrifice,
    the invoker, most rich in treasure.
    """
    
    print("🔥 Processing RV 1.1.1 (First verse of Rig Veda)")
    print("-" * 50)
    
    analysis = processor.process_rigveda_verse(rigveda_verse, translation)
    print(processor.visualize_analysis(analysis))
    
    print("\n✅ Sanskrit processing system initialized!")
    print("🚀 Ready for Step 3: Advanced Morphological Analysis")
    print("\n💡 Next: We'll integrate actual Sanskrit morphological analysis")
    print("   and connect this to modern LLMs for deeper understanding.")
