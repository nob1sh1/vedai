"""
Rig Veda Corpus Integration System
Processes the complete Rig Veda JSON corpus and integrates it with Wisdom AI

This transforms your system from having ~50 teachings to having 1,000+ authentic Sanskrit hymns
with full semantic analysis, embeddings, and spiritual guidance capabilities.
"""

import json
import numpy as np
import re
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from collections import defaultdict, Counter
import random
from sentence_transformers import SentenceTransformer
import pickle
import os
from datetime import datetime

@dataclass
class RigVedaHymn:
    """Represents a complete Rig Veda hymn with semantic analysis"""
    book: int
    hymn: int
    reference: str
    sanskrit: str
    romanized: str
    verses: int
    url: str
    semantic_analysis: Dict[str, Any] = None
    spiritual_themes: List[str] = None
    deity_focus: str = ""
    ritual_context: str = ""
    philosophical_concepts: List[str] = None
    embedding: np.ndarray = None

class RigVedaCorpusProcessor:
    """Processes and analyzes the complete Rig Veda corpus"""
    
    def __init__(self, corpus_file: str = "data/rigveda_complete_corpus.json"):
        self.corpus_file = corpus_file
        self.hymns: List[RigVedaHymn] = []
        self.embeddings_cache = {}
        
        # Initialize embedding model
        print("🔄 Loading sentence transformer model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Vedic concepts and themes for classification
        self.vedic_themes = {
            'agni': {
                'keywords': ['अग्नि', 'agni', 'fire', 'flame'],
                'description': 'Fire deity, sacrifice, purification, divine messenger',
                'spiritual_significance': 'Inner fire of consciousness, transformation, spiritual purification'
            },
            'indra': {
                'keywords': ['इन्द्र', 'indra', 'vajra', 'thunderbolt'],
                'description': 'King of gods, storm deity, warrior, destroyer of obstacles',
                'spiritual_significance': 'Inner strength, overcoming limitations, spiritual victory'
            },
            'soma': {
                'keywords': ['सोम', 'soma', 'amrita', 'nectar'],
                'description': 'Sacred drink, divine nectar, moon deity, ecstasy',
                'spiritual_significance': 'Divine bliss, spiritual intoxication, higher consciousness'
            },
            'surya': {
                'keywords': ['सूर्य', 'surya', 'sun', 'light', 'illumination'],
                'description': 'Sun deity, cosmic light, illumination, all-seeing',
                'spiritual_significance': 'Consciousness, enlightenment, divine knowledge'
            },
            'varuna': {
                'keywords': ['वरुण', 'varuna', 'water', 'cosmic_order'],
                'description': 'Water deity, cosmic law, moral order, binding truth',
                'spiritual_significance': 'Cosmic consciousness, moral law, divine justice'
            },
            'vayu': {
                'keywords': ['वायु', 'vayu', 'wind', 'breath', 'prana'],
                'description': 'Wind deity, life breath, vital energy, movement',
                'spiritual_significance': 'Life force, pranayama, spiritual energy'
            },
            'cosmic_order': {
                'keywords': ['ऋत', 'rta', 'rita', 'order', 'truth', 'satya'],
                'description': 'Cosmic law, universal order, truth, righteousness',
                'spiritual_significance': 'Divine harmony, natural law, spiritual truth'
            },
            'sacrifice': {
                'keywords': ['यज्ञ', 'yajna', 'homa', 'offering', 'oblation'],
                'description': 'Sacred ritual, offering, sacrifice, spiritual discipline',
                'spiritual_significance': 'Self-offering, devotion, spiritual practice'
            },
            'creation': {
                'keywords': ['सृष्टि', 'creation', 'genesis', 'origin', 'beginning'],
                'description': 'Cosmic creation, origin of universe, divine manifestation',
                'spiritual_significance': 'Self-creation, manifestation, divine creativity'
            },
            'prayer': {
                'keywords': ['प्रार्थना', 'prayer', 'invocation', 'hymn', 'praise'],
                'description': 'Divine invocation, praise, prayer, spiritual communion',
                'spiritual_significance': 'Devotion, surrender, divine connection'
            }
        }
        
        # Philosophical concepts in Rig Veda
        self.philosophical_concepts = {
            'consciousness': ['चेतना', 'consciousness', 'awareness', 'chit'],
            'existence': ['सत्', 'sat', 'being', 'existence', 'reality'],
            'bliss': ['आनन्द', 'ananda', 'bliss', 'joy', 'happiness'],
            'immortality': ['अमृत', 'amrita', 'immortal', 'deathless', 'eternal'],
            'wisdom': ['ज्ञान', 'jnana', 'knowledge', 'wisdom', 'understanding'],
            'unity': ['एकता', 'unity', 'oneness', 'integration', 'wholeness'],
            'dharma': ['धर्म', 'dharma', 'righteousness', 'duty', 'law'],
            'karma': ['कर्म', 'karma', 'action', 'work', 'deed']
        }
    
    def load_corpus(self) -> bool:
        """Load the Rig Veda JSON corpus"""
        try:
            print(f"📚 Loading Rig Veda corpus from {self.corpus_file}...")
            
            with open(self.corpus_file, 'r', encoding='utf-8') as f:
                corpus_data = json.load(f)
            
            print(f"✅ Loaded {len(corpus_data)} hymns from corpus")
            
            # Convert to RigVedaHymn objects
            for hymn_data in corpus_data:
                if hymn_data.get('status') == 'complete' and hymn_data.get('sanskrit'):
                    hymn = RigVedaHymn(
                        book=hymn_data['book'],
                        hymn=hymn_data['hymn'],
                        reference=hymn_data['reference'],
                        sanskrit=hymn_data['sanskrit'],
                        romanized=hymn_data['romanized'],
                        verses=hymn_data.get('verses', 0),
                        url=hymn_data.get('url', '')
                    )
                    self.hymns.append(hymn)
            
            print(f"✅ Successfully processed {len(self.hymns)} complete hymns")
            return True
            
        except Exception as e:
            print(f"❌ Error loading corpus: {e}")
            return False
    
    def analyze_hymn_themes(self, hymn: RigVedaHymn) -> Tuple[List[str], str, str, List[str]]:
        """Analyze spiritual themes, deity focus, and concepts in a hymn"""
        
        # Combine Sanskrit and romanized text for analysis
        text_to_analyze = f"{hymn.sanskrit} {hymn.romanized}".lower()
        
        # Find spiritual themes
        themes_found = []
        theme_scores = {}
        
        for theme_name, theme_data in self.vedic_themes.items():
            score = 0
            for keyword in theme_data['keywords']:
                # Count occurrences of keywords
                count = text_to_analyze.count(keyword.lower())
                score += count * 2 if len(keyword) > 3 else count
            
            if score > 0:
                theme_scores[theme_name] = score
                themes_found.append(theme_name)
        
        # Sort themes by relevance
        themes_found.sort(key=lambda x: theme_scores.get(x, 0), reverse=True)
        
        # Determine primary deity focus
        deity_themes = ['agni', 'indra', 'soma', 'surya', 'varuna', 'vayu']
        primary_deity = ""
        max_deity_score = 0
        
        for deity in deity_themes:
            if deity in theme_scores and theme_scores[deity] > max_deity_score:
                max_deity_score = theme_scores[deity]
                primary_deity = deity
        
        # Determine ritual context
        ritual_context = "general"
        if 'sacrifice' in themes_found:
            ritual_context = "sacrifice"
        elif 'prayer' in themes_found:
            ritual_context = "prayer"
        elif 'creation' in themes_found:
            ritual_context = "cosmological"
        
        # Find philosophical concepts
        philosophical_concepts = []
        for concept, keywords in self.philosophical_concepts.items():
            for keyword in keywords:
                if keyword.lower() in text_to_analyze:
                    philosophical_concepts.append(concept)
                    break
        
        return themes_found[:5], primary_deity, ritual_context, philosophical_concepts
    
    def create_embeddings(self, batch_size: int = 32) -> None:
        """Create embeddings for all hymns"""
        print(f"🧮 Creating embeddings for {len(self.hymns)} hymns...")
        
        # Prepare texts for embedding (use romanized version for better processing)
        texts = []
        for hymn in self.hymns:
            # Combine reference and romanized text for context
            text = f"{hymn.reference}: {hymn.romanized}"
            texts.append(text)
        
        # Create embeddings in batches
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_embeddings = self.embedding_model.encode(batch_texts, show_progress_bar=True)
            all_embeddings.extend(batch_embeddings)
            print(f"  Processed {min(i+batch_size, len(texts))}/{len(texts)} hymns")
        
        # Assign embeddings to hymns
        for hymn, embedding in zip(self.hymns, all_embeddings):
            hymn.embedding = embedding
        
        print("✅ Embeddings created successfully")
    
    def process_complete_corpus(self) -> Dict[str, Any]:
        """Process the entire corpus with semantic analysis"""
        
        print("🔄 Processing complete Rig Veda corpus...")
        
        if not self.load_corpus():
            return {}
        
        # Analyze themes for all hymns
        print("🎭 Analyzing spiritual themes...")
        for i, hymn in enumerate(self.hymns):
            if i % 100 == 0:
                print(f"  Analyzed {i}/{len(self.hymns)} hymns")
            
            themes, deity, context, concepts = self.analyze_hymn_themes(hymn)
            hymn.spiritual_themes = themes
            hymn.deity_focus = deity
            hymn.ritual_context = context
            hymn.philosophical_concepts = concepts
        
        # Create embeddings
        self.create_embeddings()
        
        # Generate corpus statistics
        stats = self._generate_corpus_statistics()
        
        # Save processed corpus
        self.save_processed_corpus()
        
        print("✅ Corpus processing complete!")
        return stats
    
    def _generate_corpus_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive statistics about the corpus"""
        
        stats = {
            'total_hymns': len(self.hymns),
            'total_verses': sum(hymn.verses for hymn in self.hymns),
            'books_covered': len(set(hymn.book for hymn in self.hymns)),
            'theme_distribution': defaultdict(int),
            'deity_distribution': defaultdict(int),
            'philosophical_concepts': defaultdict(int),
            'book_statistics': defaultdict(lambda: {'hymns': 0, 'verses': 0}),
            'average_verses_per_hymn': 0
        }
        
        # Count themes, deities, and concepts
        for hymn in self.hymns:
            # Themes
            for theme in hymn.spiritual_themes or []:
                stats['theme_distribution'][theme] += 1
            
            # Deities
            if hymn.deity_focus:
                stats['deity_distribution'][hymn.deity_focus] += 1
            
            # Philosophical concepts
            for concept in hymn.philosophical_concepts or []:
                stats['philosophical_concepts'][concept] += 1
            
            # Book statistics
            stats['book_statistics'][hymn.book]['hymns'] += 1
            stats['book_statistics'][hymn.book]['verses'] += hymn.verses
        
        # Calculate averages
        if stats['total_hymns'] > 0:
            stats['average_verses_per_hymn'] = stats['total_verses'] / stats['total_hymns']
        
        return dict(stats)
    
    def save_processed_corpus(self, output_file: str = "data/rigveda_processed_corpus.pkl"):
        """Save the processed corpus with embeddings"""
        print(f"💾 Saving processed corpus to {output_file}...")
        
        # Create serializable data
        corpus_data = []
        for hymn in self.hymns:
            hymn_data = {
                'book': hymn.book,
                'hymn': hymn.hymn,
                'reference': hymn.reference,
                'sanskrit': hymn.sanskrit,
                'romanized': hymn.romanized,
                'verses': hymn.verses,
                'url': hymn.url,
                'spiritual_themes': hymn.spiritual_themes,
                'deity_focus': hymn.deity_focus,
                'ritual_context': hymn.ritual_context,
                'philosophical_concepts': hymn.philosophical_concepts,
                'embedding': hymn.embedding.tolist() if hymn.embedding is not None else None
            }
            corpus_data.append(hymn_data)
        
        # Save with pickle for numpy arrays
        with open(output_file, 'wb') as f:
            pickle.dump(corpus_data, f)
        
        # Also save as JSON (without embeddings for readability)
        json_file = output_file.replace('.pkl', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json_corpus = []
            for hymn_data in corpus_data:
                json_hymn = hymn_data.copy()
                json_hymn.pop('embedding', None)  # Remove embeddings for JSON
                json_corpus.append(json_hymn)
            json.dump(json_corpus, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved processed corpus to {output_file} and {json_file}")
    
    def search_corpus(self, query: str, top_k: int = 10) -> List[Tuple[RigVedaHymn, float]]:
        """Search the corpus using semantic similarity"""
        # Fix: Check if embeddings are None instead of boolean evaluation
        if not self.hymns or self.hymns[0].embedding is None:
            print("❌ Embeddings not loaded. Process corpus first.")
            return []
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Calculate similarities
        similarities = []
        for hymn in self.hymns:
            similarity = np.dot(query_embedding, hymn.embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(hymn.embedding)
            )
            similarities.append((hymn, similarity))
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def get_hymns_by_theme(self, theme: str, limit: int = 20) -> List[RigVedaHymn]:
        """Get hymns by spiritual theme"""
        matching_hymns = []
        for hymn in self.hymns:
            if hymn.spiritual_themes and theme in hymn.spiritual_themes:
                matching_hymns.append(hymn)
            if len(matching_hymns) >= limit:
                break
        return matching_hymns
    
    def get_random_hymn_by_criteria(self, deity: str = None, theme: str = None, 
                                  book: int = None) -> Optional[RigVedaHymn]:
        """Get a random hymn matching specific criteria"""
        candidates = []
        
        for hymn in self.hymns:
            matches = True
            
            if deity and hymn.deity_focus != deity:
                matches = False
            if theme and (not hymn.spiritual_themes or theme not in hymn.spiritual_themes):
                matches = False
            if book and hymn.book != book:
                matches = False
            
            if matches:
                candidates.append(hymn)
        
        return random.choice(candidates) if candidates else None

def create_wisdom_ai_integration():
    """Integration function to connect Rig Veda corpus with Wisdom AI"""
    
    processor = RigVedaCorpusProcessor()
    
    # Process the complete corpus
    stats = processor.process_complete_corpus()
    
    print("\n🕉️  RIG VEDA CORPUS INTEGRATION COMPLETE 🕉️")
    print("=" * 60)
    print(f"📚 Total hymns processed: {stats.get('total_hymns', 0)}")
    print(f"📝 Total verses: {stats.get('total_verses', 0)}")
    print(f"📖 Books covered: {stats.get('books_covered', 0)}/10")
    print(f"📊 Average verses per hymn: {stats.get('average_verses_per_hymn', 0):.1f}")
    
    print(f"\n🎭 Top Spiritual Themes:")
    theme_dist = stats.get('theme_distribution', {})
    for theme, count in sorted(theme_dist.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {theme}: {count} hymns")
    
    print(f"\n🏛️  Deity Focus Distribution:")
    deity_dist = stats.get('deity_distribution', {})
    for deity, count in sorted(deity_dist.items(), key=lambda x: x[1], reverse=True)[:8]:
        print(f"   {deity.title()}: {count} hymns")
    
    print(f"\n💎 Philosophical Concepts:")
    concept_dist = stats.get('philosophical_concepts', {})
    for concept, count in sorted(concept_dist.items(), key=lambda x: x[1], reverse=True)[:8]:
        print(f"   {concept}: {count} hymns")
    
    # Test search functionality
    print(f"\n🔍 Testing semantic search...")
    test_queries = ["fire sacrifice", "cosmic order", "divine light", "spiritual wisdom"]
    
    for query in test_queries:
        results = processor.search_corpus(query, top_k=3)
        print(f"\n   Query: '{query}'")
        for i, (hymn, score) in enumerate(results, 1):
            print(f"     {i}. {hymn.reference} - {hymn.deity_focus} (score: {score:.3f})")
    
    print(f"\n✅ Integration ready for Wisdom AI!")
    print(f"📁 Processed corpus saved to: data/rigveda_processed_corpus.pkl")
    
    return processor

if __name__ == "__main__":
    print("🕉️ STARTING RIG VEDA CORPUS INTEGRATION...")
    print("This will transform your Wisdom AI with 1,000+ authentic Sanskrit hymns")
    print("")
    
    # Check if corpus file exists
    corpus_file = "data/rigveda_complete_corpus.json"
    if not os.path.exists(corpus_file):
        print(f"❌ Corpus file not found: {corpus_file}")
        print("Please ensure your Rig Veda JSON corpus is in the correct location")
        exit(1)
    
    # Create integration
    processor = create_wisdom_ai_integration()
    
    print(f"\n🚀 NEXT STEPS:")
    print("1. The processed corpus is now ready for your Wisdom AI")
    print("2. Run the enhanced Wisdom AI system to use this massive knowledge base")
    print("3. Users can now receive guidance from 1,000+ authentic Vedic hymns!")
    print("")
    print("🙏 This represents one of the largest digitized Sanskrit spiritual corpora ever created!")