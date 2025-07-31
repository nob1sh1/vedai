"""
Standalone Sanskrit Analysis System for Rig Veda
Works without external APIs using built-in linguistic analysis
Implements Rick Briggs' semantic framework with rule-based processing
"""

import numpy as np
import json
import re
import unicodedata
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass
from collections import defaultdict, Counter

@dataclass
class SanskritTriple:
    """Sanskrit semantic triple with karaka relations"""
    verb_root: str           # Sanskrit dhatu (verb root)
    karaka: str             # Karaka relation (karta, karma, etc.)
    word: str               # Sanskrit word in context
    devanagari: str = ""    # Original Devanagari text
    meaning: str = ""       # English meaning
    confidence: float = 0.8 # Confidence in analysis
    
    def __str__(self):
        return f"{self.verb_root}, {self.karaka}, {self.word}"

@dataclass
class VedicConcept:
    """Represents a concept from Vedic literature"""
    sanskrit_term: str
    devanagari: str
    semantic_field: str     # ritual, cosmology, deity, etc.
    related_terms: List[str]
    verses: List[str]       # References where it appears

class StandaloneSanskritAnalyzer:
    """
    Comprehensive Sanskrit analyzer using rule-based linguistics
    No external APIs required - pure computational linguistics
    """
    
    def __init__(self):
        self.triples: List[SanskritTriple] = []
        self.concepts: Dict[str, VedicConcept] = {}
        self.word_frequencies: Counter = Counter()
        self.knowledge_graph: Dict[str, Any] = defaultdict(list)
        
        # Initialize Vedic knowledge base
        self._initialize_vedic_knowledge()
        self._initialize_morphological_patterns()
    
    def _initialize_vedic_knowledge(self):
        """Initialize comprehensive Vedic knowledge base"""
        
        # Deities and divine concepts
        deities = {
            'अग्नि': {'meaning': 'fire god, divine fire', 'domain': 'fire', 'attributes': ['priest', 'messenger', 'purifier']},
            'इन्द्र': {'meaning': 'king of gods, storm god', 'domain': 'storm', 'attributes': ['warrior', 'vritrahan', 'powerful']},
            'वरुण': {'meaning': 'god of waters, cosmic order', 'domain': 'water', 'attributes': ['judge', 'binding', 'rta-keeper']},
            'सोम': {'meaning': 'sacred drink, moon god', 'domain': 'soma', 'attributes': ['immortal', 'ecstatic', 'purifying']},
            'सूर्य': {'meaning': 'sun god', 'domain': 'sun', 'attributes': ['illuminating', 'all-seeing', 'life-giving']},
            'वाय': {'meaning': 'wind god', 'domain': 'air', 'attributes': ['swift', 'life-breath', 'moving']},
            'मित्र': {'meaning': 'god of friendship, contracts', 'domain': 'social', 'attributes': ['friendly', 'binding', 'loyal']}
        }
        
        # Ritual terminology  
        ritual_terms = {
            'यज्ञ': {'meaning': 'sacrifice, ritual offering', 'domain': 'ritual', 'type': 'ceremony'},
            'होम': {'meaning': 'fire offering', 'domain': 'ritual', 'type': 'fire_ritual'},
            'हवि': {'meaning': 'oblation, offering', 'domain': 'ritual', 'type': 'offering'},
            'मन्त्र': {'meaning': 'sacred formula, hymn', 'domain': 'ritual', 'type': 'speech'},
            'स्तोम': {'meaning': 'praise, hymn', 'domain': 'ritual', 'type': 'praise'},
            'होतृ': {'meaning': 'priest who invokes', 'domain': 'ritual', 'type': 'priest'},
            'ऋत्विज्': {'meaning': 'ritual priest', 'domain': 'ritual', 'type': 'priest'}
        }
        
        # Cosmic and philosophical concepts
        cosmic_terms = {
            'रित': {'meaning': 'cosmic order, truth', 'domain': 'philosophy', 'type': 'principle'},
            'सत्': {'meaning': 'being, truth', 'domain': 'philosophy', 'type': 'principle'},
            'द्यु': {'meaning': 'heaven, sky', 'domain': 'cosmology', 'type': 'realm'},
            'पृथिवी': {'meaning': 'earth', 'domain': 'cosmology', 'type': 'realm'},
            'आकाश': {'meaning': 'space, ether', 'domain': 'cosmology', 'type': 'element'},
            'कल्प': {'meaning': 'cosmic age', 'domain': 'time', 'type': 'period'}
        }
        
        # Combine all knowledge
        self.vedic_vocabulary = {**deities, **ritual_terms, **cosmic_terms}
        
        # Common verb roots (dhatus) in Rig Veda
        self.verb_roots = {
            'गम्': 'to go, move',
            'अस्': 'to be, exist', 
            'भू': 'to become, be',
            'कृ': 'to do, make',
            'दा': 'to give',
            'यज्': 'to sacrifice, worship',
            'स्तु': 'to praise',
            'गै': 'to sing',
            'वच्': 'to speak',
            'जि': 'to conquer, win',
            'इ': 'to go',
            'हन्': 'to strike, kill',
            'पा': 'to protect',
            'धा': 'to place, hold',
            'इड्': 'to praise, invoke'
        }
        
        # Karaka relations (Paninian cases)
        self.karaka_relations = {
            'कर्ता': 'agent (who does the action)',
            'कर्म': 'patient (what receives action)', 
            'करण': 'instrument (means of action)',
            'सम्प्रदान': 'recipient (to whom given)',
            'अपादान': 'source (from which separated)',
            'अधिकरण': 'location/time (where/when)',
            'सम्बन्ध': 'possessor (whose, of what)'
        }
    
    def _initialize_morphological_patterns(self):
        """Initialize Sanskrit morphological analysis patterns"""
        
        # Case ending patterns (simplified)
        self.case_endings = {
            # Nominative (karta - agent)
            'nominative': ['अः', 'आः', 'ा', 'इः', 'ी', 'उः', 'ऊः'],
            # Accusative (karma - object) 
            'accusative': ['अम्', 'आम्', 'इम्', 'ीम्', 'उम्', 'ऊम्'],
            # Instrumental (karana - instrument)
            'instrumental': ['एन', 'आ', 'इणा', 'ीणा', 'उणा', 'ऊणा'],
            # Dative (sampradana - recipient)
            'dative': ['आय', 'ए', 'ये'],
            # Ablative (apadana - source)
            'ablative': ['आत्', 'स्मात्', 'त्'],
            # Locative (adhikarana - location)
            'locative': ['े', 'इ', 'औ', 'सु']
        }
        
        # Verb conjugation patterns
        self.verb_patterns = {
            'present_3rd_sing': ['ति', 'ते'],
            'past_3rd_sing': ['त्', 'ीत्'],
            'imperative': ['तु', 'ताम्'],
            'infinitive': ['तुम्', 'ितुम्']
        }
    
    def romanize_devanagari(self, text: str) -> str:
        """Convert Devanagari to romanized Sanskrit (IAST)"""
        # Comprehensive romanization mapping
        char_map = {
            'अ': 'a', 'आ': 'ā', 'इ': 'i', 'ई': 'ī', 'उ': 'u', 'ऊ': 'ū', 'ऋ': 'ṛ', 'ॠ': 'ṝ',
            'ऌ': 'ḷ', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
            'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha', 'ङ': 'ṅa',
            'च': 'ca', 'छ': 'cha', 'ज': 'ja', 'झ': 'jha', 'ञ': 'ña',
            'ट': 'ṭa', 'ठ': 'ṭha', 'ड': 'ḍa', 'ढ': 'ḍha', 'ण': 'ṇa',
            'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha', 'न': 'na',
            'प': 'pa', 'फ': 'pha', 'ब': 'ba', 'भ': 'bha', 'म': 'ma',
            'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va',
            'श': 'śa', 'ष': 'ṣa', 'स': 'sa', 'ह': 'ha',
            'ं': 'ṃ', 'ः': 'ḥ', '्': '', '।': ' | ', '॥': ' || '
        }
        
        result = ""
        for char in text:
            result += char_map.get(char, char)
        
        return result.strip()
    
    def analyze_morphology(self, word: str) -> Dict[str, Any]:
        """Analyze morphological structure of Sanskrit word"""
        analysis = {
            'word': word,
            'possible_roots': [],
            'case': 'unknown',
            'number': 'unknown',
            'confidence': 0.0
        }
        
        # Check for verb roots
        for root, meaning in self.verb_roots.items():
            if root in word or word.startswith(root.replace('्', '')):
                analysis['possible_roots'].append({
                    'root': root,
                    'meaning': meaning,
                    'type': 'verb'
                })
                analysis['confidence'] += 0.3
        
        # Check case endings
        for case, endings in self.case_endings.items():
            for ending in endings:
                if word.endswith(ending):
                    analysis['case'] = case
                    analysis['confidence'] += 0.4
                    break
        
        return analysis
    
    def extract_semantic_triples(self, sentence: str, translation: str = "") -> List[SanskritTriple]:
        """Extract semantic triples using rule-based analysis"""
        words = re.findall(r'[^\s।॥]+', sentence)
        triples = []
        
        # Find main verb
        main_verb = None
        verb_root = None
        
        for word in words:
            morphology = self.analyze_morphology(word)
            
            # Check if word contains verb root
            for root_info in morphology['possible_roots']:
                if root_info['type'] == 'verb':
                    main_verb = word
                    verb_root = root_info['root']
                    break
            
            if main_verb:
                break
        
        # If no verb found, use common patterns
        if not verb_root:
            # Look for common Vedic verbs
            for word in words:
                if any(vr in word for vr in ['इड्', 'स्तु', 'यज्', 'गै']):
                    verb_root = 'स्तु'  # Default to 'praise'
                    main_verb = word
                    break
        
        if not verb_root:
            verb_root = 'अस्'  # Default to 'be'
            main_verb = words[0] if words else 'unknown'
        
        # Analyze each word for karaka relations
        for word in words:
            if word == main_verb:
                continue
                
            morphology = self.analyze_morphology(word)
            
            # Determine likely karaka based on case
            karaka = 'कर्ता'  # Default to agent
            if morphology['case'] == 'accusative':
                karaka = 'कर्म'
            elif morphology['case'] == 'instrumental':
                karaka = 'करण'
            elif morphology['case'] == 'dative':
                karaka = 'सम्प्रदान'
            elif morphology['case'] == 'ablative':
                karaka = 'अपादान'
            elif morphology['case'] == 'locative':
                karaka = 'अधिकरण'
            
            # Get meaning from vocabulary
            meaning = ""
            if word in self.vedic_vocabulary:
                meaning = self.vedic_vocabulary[word]['meaning']
            
            triple = SanskritTriple(
                verb_root=verb_root,
                karaka=karaka,
                word=word,
                devanagari=word,
                meaning=meaning,
                confidence=morphology['confidence']
            )
            
            triples.append(triple)
            self.triples.append(triple)
        
        return triples
    
    def classify_semantic_field(self, sentence: str) -> str:
        """Classify the semantic domain of the text"""
        words = re.findall(r'[^\s।॥]+', sentence)
        
        field_scores = defaultdict(int)
        
        for word in words:
            if word in self.vedic_vocabulary:
                domain = self.vedic_vocabulary[word].get('domain', 'unknown')
                field_scores[domain] += 1
        
        if field_scores:
            return max(field_scores, key=field_scores.get)
        return 'general'
    
    def build_knowledge_graph(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Build knowledge graph from analyses"""
        graph = {
            'entities': defaultdict(lambda: {'verses': [], 'relations': [], 'domain': 'unknown'}),
            'relationships': [],
            'domains': defaultdict(list)
        }
        
        for analysis in analyses:
            verse_ref = analysis.get('reference', 'unknown')
            
            for triple in analysis.get('triples', []):
                entity = triple.word
                
                # Add entity information
                graph['entities'][entity]['verses'].append(verse_ref)
                graph['entities'][entity]['relations'].append(triple.karaka)
                
                if triple.meaning:
                    if entity in self.vedic_vocabulary:
                        domain = self.vedic_vocabulary[entity].get('domain', 'unknown')
                        graph['entities'][entity]['domain'] = domain
                        graph['domains'][domain].append(verse_ref)
                
                # Add relationship
                relationship = {
                    'verb': triple.verb_root,
                    'relation': triple.karaka,
                    'entity': entity,
                    'verse': verse_ref,
                    'confidence': triple.confidence
                }
                graph['relationships'].append(relationship)
        
        return dict(graph)
    
    def analyze_rigveda_verse(self, sanskrit: str, translation: str = "", reference: str = "") -> Dict[str, Any]:
        """Complete analysis of a Rig Veda verse"""
        
        print(f"🔍 Analyzing: {reference}")
        print(f"📜 Sanskrit: {sanskrit}")
        
        # Extract semantic triples
        triples = self.extract_semantic_triples(sanskrit, translation)
        
        # Classify semantic field
        semantic_field = self.classify_semantic_field(sanskrit)
        
        # Romanize for analysis
        romanized = self.romanize_devanagari(sanskrit)
        
        analysis = {
            'reference': reference,
            'sanskrit': sanskrit,
            'romanized': romanized,
            'translation': translation,
            'triples': triples,
            'semantic_field': semantic_field,
            'entities_found': len([t for t in triples if t.word in self.vedic_vocabulary]),
            'confidence': np.mean([t.confidence for t in triples]) if triples else 0.0
        }
        
        print(f"✅ Found {len(triples)} semantic relations")
        print(f"🏷️  Domain: {semantic_field}")
        print(f"📈 Confidence: {analysis['confidence']:.2f}")
        
        return analysis
    
    def query_knowledge_graph(self, query: str, graph: Dict) -> List[Dict]:
        """Query the knowledge graph"""
        results = []
        query_words = query.lower().split()
        
        for relationship in graph.get('relationships', []):
            score = 0
            for word in query_words:
                # Check entity
                if word in relationship['entity'].lower():
                    score += 2
                # Check verb root  
                if word in relationship['verb'].lower():
                    score += 1.5
                # Check relation
                if word in relationship['relation'].lower():
                    score += 1
            
            if score > 0:
                results.append({
                    'relationship': relationship,
                    'score': score
                })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)[:10]
    
    def visualize_analysis(self, analysis: Dict) -> str:
        """Create text visualization of analysis"""
        output = f"🕉️ VEDIC ANALYSIS: {analysis['reference']} 🕉️\n"
        output += "=" * 50 + "\n\n"
        
        output += f"📜 Sanskrit: {analysis['sanskrit']}\n"
        output += f"🔤 Romanized: {analysis['romanized']}\n"
        
        if analysis['translation']:
            output += f"🌍 Translation: {analysis['translation']}\n"
        
        output += f"🏷️  Semantic Field: {analysis['semantic_field']}\n"
        output += f"📈 Confidence: {analysis['confidence']:.2f}\n\n"
        
        output += f"🔗 Karaka Analysis ({len(analysis['triples'])} relations):\n"
        for i, triple in enumerate(analysis['triples'], 1):
            karaka_meaning = self.karaka_relations.get(triple.karaka, triple.karaka)
            output += f"  {i:2d}. {triple.verb_root} → {triple.karaka} → {triple.word}"
            if triple.meaning:
                output += f" ({triple.meaning})"
            output += f" [conf: {triple.confidence:.2f}]\n"
            output += f"      Relation: {karaka_meaning}\n"
        
        return output

# Main demonstration
if __name__ == "__main__":
    print("🕉️ STANDALONE SANSKRIT ANALYSIS SYSTEM 🕉️")
    print("Based on Rick Briggs' 1985 Research")
    print("No external APIs required!")
    print("=" * 70)
    
    # Initialize analyzer
    analyzer = StandaloneSanskritAnalyzer()
    
    # Sample Rig Veda verses
    rigveda_corpus = [
        {
            'sanskrit': 'अग्निमीळे पुरोहितं यज्ञस्य देवमृत्विजम्',
            'translation': 'I praise Agni, the priest, the divine minister of sacrifice',
            'reference': 'RV 1.1.1a'
        },
        {
            'sanskrit': 'होतारं रत्नधातमम्',
            'translation': 'the invoker, most rich in treasure',
            'reference': 'RV 1.1.1b'
        },
        {
            'sanskrit': 'इन्द्रं मित्रं वरुणमग्निमाहुः',
            'translation': 'They call him Indra, Mitra, Varuna, Agni',
            'reference': 'RV 1.164.46a'
        }
    ]
    
    # Analyze each verse
    analyses = []
    for verse in rigveda_corpus:
        analysis = analyzer.analyze_rigveda_verse(
            verse['sanskrit'],
            verse['translation'], 
            verse['reference']
        )
        analyses.append(analysis)
        
        # Show detailed analysis
        print(f"\n{analyzer.visualize_analysis(analysis)}")
    
    # Build knowledge graph
    print("🕸️  Building Knowledge Graph...")
    knowledge_graph = analyzer.build_knowledge_graph(analyses)
    
    print(f"\n📊 Knowledge Graph Summary:")
    print(f"   Entities: {len(knowledge_graph['entities'])}")
    print(f"   Relationships: {len(knowledge_graph['relationships'])}")
    print(f"   Semantic domains: {list(knowledge_graph['domains'].keys())}")
    
    # Example queries
    print(f"\n🔍 Example Queries:")
    queries = ["agni fire", "indra", "sacrifice ritual", "priest"]
    
    for query in queries:
        results = analyzer.query_knowledge_graph(query, knowledge_graph)
        print(f"\n   Query: '{query}' - {len(results)} results")
        for i, result in enumerate(results[:3], 1):
            rel = result['relationship']
            print(f"     {i}. {rel['entity']} ({rel['relation']}) in {rel['verse']} [score: {result['score']:.1f}]")
    
    # Save analysis
    output_file = 'data/rigveda_standalone_analysis.json'
    analysis_data = {
        'analyses': [
            {**analysis, 'triples': [
                {
                    'verb_root': t.verb_root,
                    'karaka': t.karaka, 
                    'word': t.word,
                    'meaning': t.meaning,
                    'confidence': t.confidence
                } for t in analysis['triples']
            ]} for analysis in analyses
        ],
        'knowledge_graph': knowledge_graph,
        'vocabulary_size': len(analyzer.vedic_vocabulary)
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Analysis saved to {output_file}")
    print(f"✅ Standalone Sanskrit analysis system ready!")
    print(f"🚀 No external APIs needed - pure computational linguistics!")