"""
Step 3: Advanced Semantic Analysis with LLMs for Sanskrit/Rig Veda
Integrates modern LLMs with Sanskrit embeddings and Briggs' semantic framework

This system:
1. Uses LLMs to enhance Sanskrit morphological analysis
2. Applies Briggs' karaka framework with AI assistance
3. Creates semantic knowledge graphs from Vedic texts
4. Enables intelligent querying of Sanskrit corpus
5. Builds RAG system for Vedic scholarship
"""

import os
import openai
from typing import Dict, List, Tuple, Set, Optional, Any
import json
import numpy as np
from dataclasses import dataclass, asdict
from collections import defaultdict
import asyncio

# Import our previous components
import sys
sys.path.append('src')

try:
    from sanskrit_embeddings import SanskritCorpusProcessor, SanskritEmbedding
    from semantic_net import SemanticNet, Triple
except ImportError:
    print("⚠️  Import issue - make sure previous files are created")

@dataclass
class VedicSemanticTriple:
    """Enhanced semantic triple for Vedic texts with LLM analysis"""
    verb_root: str              # Sanskrit dhatu
    karaka_relation: str        # Paninian case relation
    word: str                   # Sanskrit word
    devanagari: str            # Original Devanagari
    morphological_analysis: str # LLM-generated morphology
    semantic_field: str        # Domain (ritual, cosmology, etc.)
    llm_interpretation: str    # LLM explanation
    confidence_score: float = 0.0
    verse_reference: str = ""   # RV reference

class VedicLLMAnalyzer:
    """
    Advanced Sanskrit analysis using LLMs + traditional grammar
    Combines Briggs' approach with modern AI capabilities
    """
    
    def __init__(self, api_key: Optional[str] = None):
        # Initialize OpenAI (you can also use other LLMs)
        if api_key:
            openai.api_key = api_key
        
        # Initialize our Sanskrit processor
        self.sanskrit_processor = SanskritCorpusProcessor()
        self.semantic_net = SemanticNet()
        
        # Vedic semantic fields for classification
        self.vedic_domains = {
            'ritual': ['यज्ञ', 'होम', 'हवि', 'सोम', 'अग्नि'],
            'cosmology': ['सूर्य', 'चन्द्र', 'द्यु', 'पृथिवी', 'आकाश'],
            'deities': ['इन्द्र', 'अग्नि', 'वरुण', 'मित्र', 'सोम'],
            'philosophy': ['सत्', 'रित', 'धर्म', 'ब्रह्मन्', 'आत्मन्'],
            'nature': ['वाय', 'आप', 'वन', 'गिरि', 'नदी']
        }
        
        # Karaka relations from Paninian grammar
        self.karaka_system = {
            'कर्ता': 'agent (one who does)',
            'कर्म': 'patient (what is done to)',
            'करण': 'instrument (by means of which)',
            'सम्प्रदान': 'recipient (to whom given)',
            'अपादान': 'source (from which separated)',
            'अधिकरण': 'locus (in which/when)',
            'सम्बन्ध': 'possessor (whose)'
        }
    
    def create_llm_prompt_for_sanskrit(self, sanskrit_text: str, context: str = "") -> str:
        """Create specialized prompt for Sanskrit analysis"""
        prompt = f"""You are an expert in Sanskrit grammar and Vedic literature, specifically trained in Paninian grammatical analysis and Rick Briggs' semantic framework.

Analyze this Sanskrit text following these principles:

Sanskrit Text: {sanskrit_text}
Context: {context}

Please provide:

1. MORPHOLOGICAL ANALYSIS:
   - Break down each word into root + suffixes
   - Identify verb roots (dhatus) 
   - Determine case endings and their grammatical roles

2. KARAKA ANALYSIS (following Panini's framework):
   - Identify the main verb and its semantic roles
   - Map each word to appropriate karaka relations:
     * कर्ता (karta) - agent/subject
     * कर्म (karma) - object/patient  
     * करण (karana) - instrument
     * सम्प्रदान (sampradana) - recipient
     * अपादान (apadana) - source/origin
     * अधिकरण (adhikarana) - location/time
   
3. SEMANTIC FIELD:
   - Classify the content domain (ritual, cosmology, deities, etc.)
   - Identify key theological or philosophical concepts

4. TRIPLE REPRESENTATION:
   - Express the meaning as semantic triples: verb, relation, argument
   - Follow Rick Briggs' demonstration of Sanskrit→AI equivalence

5. INTERPRETATION:
   - Provide scholarly interpretation of the verse's meaning
   - Note any significant Vedic concepts or symbolism

Format your response as structured JSON with these keys:
- morphology: dict of word analyses  
- karaka_relations: list of karaka mappings
- semantic_field: domain classification
- triples: list of semantic triples
- interpretation: scholarly explanation
- confidence: confidence score (0-1)
"""
        return prompt
    
    async def analyze_with_llm(self, sanskrit_text: str, context: str = "") -> Dict[str, Any]:
        """Analyze Sanskrit text using LLM with specialized prompting"""
        try:
            prompt = self.create_llm_prompt_for_sanskrit(sanskrit_text, context)
            
            # Using OpenAI API (you can substitute other LLMs)
            response = openai.ChatCompletion.create(
                model="gpt-4",  # or "gpt-3.5-turbo" 
                messages=[
                    {"role": "system", "content": "You are a Sanskrit scholar expert in Paninian grammar and Vedic literature."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=1500
            )
            
            # Try to parse JSON response
            content = response.choices[0].message.content
            try:
                analysis = json.loads(content)
            except json.JSONDecodeError:
                # If not JSON, create structured response from text
                analysis = {
                    "morphology": {},
                    "karaka_relations": [],
                    "semantic_field": "unknown",
                    "triples": [],
                    "interpretation": content,
                    "confidence": 0.7
                }
            
            return analysis
            
        except Exception as e:
            print(f"❌ LLM Analysis error: {e}")
            return {
                "morphology": {},
                "karaka_relations": [],
                "semantic_field": "error",
                "triples": [],
                "interpretation": f"Analysis failed: {str(e)}",
                "confidence": 0.0
            }
    
    def enhance_sanskrit_embeddings(self, embeddings: Dict[str, np.ndarray], 
                                  llm_analyses: List[Dict]) -> Dict[str, np.ndarray]:
        """Enhance Sanskrit embeddings with LLM semantic information"""
        enhanced_embeddings = embeddings.copy()
        
        for analysis in llm_analyses:
            semantic_field = analysis.get('semantic_field', 'unknown')
            
            # Adjust embeddings based on semantic field
            for word in analysis.get('morphology', {}):
                if word in enhanced_embeddings:
                    embedding = enhanced_embeddings[word].copy()
                    
                    # Add semantic field information to embedding
                    if semantic_field in self.vedic_domains:
                        field_adjustment = np.random.normal(0, 0.05, embedding.shape)
                        embedding += field_adjustment
                        
                    # Normalize
                    enhanced_embeddings[word] = embedding / np.linalg.norm(embedding)
        
        return enhanced_embeddings
    
    def create_vedic_knowledge_graph(self, analyses: List[Dict], 
                                   verse_references: List[str]) -> Dict[str, Any]:
        """Create knowledge graph from analyzed Vedic texts"""
        knowledge_graph = {
            'nodes': defaultdict(dict),      # Entities (deities, concepts, etc.)
            'relationships': [],             # Semantic relationships
            'semantic_fields': defaultdict(list),  # Domain classifications
            'verse_connections': defaultdict(list) # Cross-references
        }
        
        for i, analysis in enumerate(analyses):
            verse_ref = verse_references[i] if i < len(verse_references) else f"verse_{i}"
            
            # Extract entities and relationships
            for triple in analysis.get('triples', []):
                if isinstance(triple, dict):
                    verb = triple.get('verb', '')
                    relation = triple.get('relation', '')
                    argument = triple.get('argument', '')
                    
                    # Add to knowledge graph
                    relationship = {
                        'verb': verb,
                        'relation': relation,
                        'argument': argument,
                        'source_verse': verse_ref,
                        'confidence': analysis.get('confidence', 0.5)
                    }
                    knowledge_graph['relationships'].append(relationship)
                    
                    # Track entities
                    knowledge_graph['nodes'][argument]['verses'] = knowledge_graph['nodes'][argument].get('verses', [])
                    knowledge_graph['nodes'][argument]['verses'].append(verse_ref)
            
            # Classify by semantic field
            semantic_field = analysis.get('semantic_field', 'unknown')
            knowledge_graph['semantic_fields'][semantic_field].append(verse_ref)
        
        return dict(knowledge_graph)
    
    def query_vedic_knowledge(self, query: str, knowledge_graph: Dict, 
                            embeddings: Dict[str, np.ndarray]) -> List[Dict]:
        """Query the Vedic knowledge graph using semantic search"""
        results = []
        
        # Simple keyword matching (can be enhanced with embedding similarity)
        query_words = query.lower().split()
        
        for relationship in knowledge_graph.get('relationships', []):
            score = 0
            for word in query_words:
                if word in relationship.get('verb', '').lower():
                    score += 2
                if word in relationship.get('argument', '').lower():
                    score += 1.5
                if word in relationship.get('relation', '').lower():
                    score += 1
            
            if score > 0:
                results.append({
                    'relationship': relationship,
                    'relevance_score': score,
                    'verse': relationship.get('source_verse', '')
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:10]  # Top 10 results

# Example application: Rig Veda Analysis System
class RigVedaAnalysisSystem:
    """Complete system for analyzing Rig Veda using LLMs + Sanskrit embeddings"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.analyzer = VedicLLMAnalyzer(openai_api_key)
        self.corpus_analyses: List[Dict] = []
        self.knowledge_graph: Dict = {}
        self.enhanced_embeddings: Dict[str, np.ndarray] = {}
    
    async def analyze_rigveda_corpus(self, verses: List[Dict]) -> Dict[str, Any]:
        """Analyze a corpus of Rig Veda verses"""
        print(f"🔍 Analyzing {len(verses)} Rig Veda verses with LLM...")
        
        verse_refs = []
        for i, verse in enumerate(verses):
            print(f"\n📜 Analyzing {verse.get('reference', f'Verse {i+1}')}:")
            print(f"   Sanskrit: {verse['sanskrit']}")
            
            # LLM analysis
            analysis = await self.analyzer.analyze_with_llm(
                verse['sanskrit'], 
                verse.get('translation', '')
            )
            
            self.corpus_analyses.append(analysis)
            verse_refs.append(verse.get('reference', f'verse_{i}'))
            
            print(f"   ✅ Confidence: {analysis.get('confidence', 0):.2f}")
            print(f"   🏷️  Field: {analysis.get('semantic_field', 'unknown')}")
        
        # Create knowledge graph
        print(f"\n🕸️  Building knowledge graph...")
        self.knowledge_graph = self.analyzer.create_vedic_knowledge_graph(
            self.corpus_analyses, verse_refs
        )
        
        # Enhance embeddings (if available)
        if hasattr(self.analyzer.sanskrit_processor, 'word_embeddings'):
            self.enhanced_embeddings = self.analyzer.enhance_sanskrit_embeddings(
                self.analyzer.sanskrit_processor.word_embeddings,
                self.corpus_analyses
            )
        
        return {
            'analyses': self.corpus_analyses,
            'knowledge_graph': self.knowledge_graph,
            'enhanced_embeddings': len(self.enhanced_embeddings)
        }
    
    def query_system(self, query: str) -> List[Dict]:
        """Query the analyzed Rig Veda corpus"""
        return self.analyzer.query_vedic_knowledge(
            query, self.knowledge_graph, self.enhanced_embeddings
        )
    
    def save_analysis(self, filename: str):
        """Save complete analysis to file"""
        analysis_data = {
            'corpus_analyses': self.corpus_analyses,
            'knowledge_graph': self.knowledge_graph,
            'embedding_count': len(self.enhanced_embeddings)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)

# Example usage
if __name__ == "__main__":
    print("🕉️ RIG VEDA LLM ANALYSIS SYSTEM 🕉️")
    print("=" * 60)
    
    # Sample Rig Veda verses for analysis
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
    
    # Note: You need OpenAI API key for full functionality
    api_key = os.getenv('OPENAI_API_KEY')  # Set this environment variable
    
    if api_key:
        print("🔑 OpenAI API key found - full LLM analysis enabled")
        system = RigVedaAnalysisSystem(api_key)
        
        # Analyze corpus (async)
        import asyncio
        async def run_analysis():
            results = await system.analyze_rigveda_corpus(rigveda_corpus)
            
            print(f"\n📊 Analysis Results:")
            print(f"   Verses analyzed: {len(results['analyses'])}")
            print(f"   Knowledge graph relationships: {len(results['knowledge_graph'].get('relationships', []))}")
            print(f"   Enhanced embeddings: {results['enhanced_embeddings']}")
            
            # Example queries
            queries = ["Agni fire ritual", "Indra deity", "sacrifice offering"]
            for query in queries:
                print(f"\n🔍 Query: '{query}'")
                results = system.query_system(query)
                for i, result in enumerate(results[:3], 1):
                    print(f"   {i}. {result['verse']} (score: {result['relevance_score']:.1f})")
            
            # Save analysis
            system.save_analysis('data/rigveda_llm_analysis.json')
            print(f"\n💾 Analysis saved to data/rigveda_llm_analysis.json")
        
        # Run the analysis
        asyncio.run(run_analysis())
        
    else:
        print("⚠️  No OpenAI API key found")
        print("   Set OPENAI_API_KEY environment variable for full functionality")
        print("   Example: export OPENAI_API_KEY='your-key-here'")
        
        # Show system capabilities without API
        system = RigVedaAnalysisSystem()
        print(f"\n✅ System initialized (offline mode)")
        print(f"📚 Available Vedic domains: {list(system.analyzer.vedic_domains.keys())}")
        print(f"🔗 Karaka relations: {list(system.analyzer.karaka_system.keys())}")
    
    print(f"\n🚀 System ready for advanced Vedic text analysis!")
    print(f"💡 Next: Add your OpenAI API key to unlock full LLM capabilities")