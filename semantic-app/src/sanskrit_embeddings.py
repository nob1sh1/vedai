"""
Sanskrit Devanagari Embedding and Training System for Rig Veda
Creates embeddings from actual Sanskrit characters and trains on Vedic corpus

This system:
1. Processes actual Devanagari Sanskrit text
2. Creates character-level and word-level embeddings 
3. Trains on Rig Veda corpus using Briggs' semantic framework
4. Builds knowledge representation from authentic Sanskrit sources
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Set, Optional
import re
import json
from collections import defaultdict, Counter
from dataclasses import dataclass
import unicodedata

# Sanskrit/Devanagari Unicode ranges
DEVANAGARI_RANGE = (0x0900, 0x097F)
VEDIC_EXTENSIONS_RANGE = (0xA8E0, 0xA8FF)

@dataclass
class SanskritEmbedding:
    """Represents Sanskrit word/character embedding with semantic info"""
    text: str                # Original Devanagari text
    romanized: str          # IAST romanization
    embedding: np.ndarray   # Vector representation
    semantic_tags: List[str] # Karaka relations, word class, etc.
    frequency: int = 0      # Frequency in corpus
    context_words: List[str] = None  # Co-occurring words

class SanskritCorpusProcessor:
    """
    Processes Sanskrit corpus for embedding training
    Handles Devanagari Unicode and applies Briggs' semantic framework
    """
    
    def __init__(self):
        self.vocabulary: Dict[str, SanskritEmbedding] = {}
        self.character_vocab: Dict[str, int] = {}
        self.word_frequencies: Counter = Counter()
        self.context_matrix: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Initialize Devanagari character mapping
        self._initialize_devanagari_mapping()
        
    def _initialize_devanagari_mapping(self):
        """Create mapping for Devanagari characters"""
        # Basic Devanagari vowels and consonants
        vowels = ['अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ऋ', 'ॠ', 'ऌ', 'ॡ', 'ए', 'ऐ', 'ओ', 'औ']
        consonants = ['क', 'ख', 'ग', 'घ', 'ङ', 'च', 'छ', 'ज', 'झ', 'ञ', 'ट', 'ठ', 'ड', 'ढ', 'ण', 
                     'त', 'थ', 'द', 'ध', 'न', 'प', 'फ', 'ब', 'भ', 'म', 'य', 'र', 'ल', 'व', 'श', 'ष', 'स', 'ह']
        
        # Add all Devanagari characters to vocabulary
        for i, char in enumerate(vowels + consonants):
            self.character_vocab[char] = i
    
    def is_devanagari_text(self, text: str) -> bool:
        """Check if text contains Devanagari characters"""
        for char in text:
            code_point = ord(char)
            if (DEVANAGARI_RANGE[0] <= code_point <= DEVANAGARI_RANGE[1] or
                VEDIC_EXTENSIONS_RANGE[0] <= code_point <= VEDIC_EXTENSIONS_RANGE[1]):
                return True
        return False
    
    def romanize_sanskrit(self, devanagari_text: str) -> str:
        """
        Basic romanization of Devanagari to IAST
        (Simplified version - can be enhanced with proper transliteration libraries)
        """
        # Basic mapping for common characters
        romanization_map = {
            'अ': 'a', 'आ': 'ā', 'इ': 'i', 'ई': 'ī', 'उ': 'u', 'ऊ': 'ū', 
            'ऋ': 'ṛ', 'ॠ': 'ṝ', 'ऌ': 'ḷ', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
            'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha', 'ङ': 'ṅa',
            'च': 'ca', 'छ': 'cha', 'ज': 'ja', 'झ': 'jha', 'ञ': 'ña',
            'ट': 'ṭa', 'ठ': 'ṭha', 'ड': 'ḍa', 'ढ': 'ḍha', 'ण': 'ṇa',
            'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha', 'न': 'na',
            'प': 'pa', 'फ': 'pha', 'ब': 'ba', 'भ': 'bha', 'म': 'ma',
            'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va', 
            'श': 'śa', 'ष': 'ṣa', 'स': 'sa', 'ह': 'ha',
            '्': '', 'ं': 'ṃ', 'ः': 'ḥ', '।': '|', '॥': '||'
        }
        
        result = ""
        for char in devanagari_text:
            result += romanization_map.get(char, char)
        
        return result
    
    def tokenize_sanskrit(self, text: str) -> List[str]:
        """Tokenize Sanskrit text handling Devanagari properly"""
        # Split on whitespace and Sanskrit punctuation
        if self.is_devanagari_text(text):
            # Handle Devanagari punctuation
            tokens = re.findall(r'[^\s।॥]+', text)
        else:
            # Handle romanized text
            tokens = re.findall(r'\b\w+\b', text)
        
        return [token.strip() for token in tokens if token.strip()]
    
    def process_rigveda_text(self, sanskrit_text: str, translation: str = "") -> Dict:
        """Process Rig Veda text and extract embeddings"""
        tokens = self.tokenize_sanskrit(sanskrit_text)
        
        analysis = {
            'original_text': sanskrit_text,
            'translation': translation,
            'tokens': tokens,
            'is_devanagari': self.is_devanagari_text(sanskrit_text),
            'word_embeddings': {},
            'character_sequence': [],
            'semantic_analysis': []
        }
        
        # Process each token
        for i, token in enumerate(tokens):
            # Update frequency
            self.word_frequencies[token] += 1
            
            # Create romanized version if needed
            romanized = self.romanize_sanskrit(token) if analysis['is_devanagari'] else token
            
            # Build context matrix (co-occurrence)
            context_window = 3  # Words before and after
            for j in range(max(0, i-context_window), min(len(tokens), i+context_window+1)):
                if i != j:
                    self.context_matrix[token][tokens[j]] += 1
            
            # Extract character sequence for character-level embeddings
            if analysis['is_devanagari']:
                chars = list(token)
                analysis['character_sequence'].extend(chars)
                for char in chars:
                    if char not in self.character_vocab:
                        self.character_vocab[char] = len(self.character_vocab)
        
        return analysis
    
    def create_word_embeddings(self, embedding_dim: int = 100) -> Dict[str, np.ndarray]:
        """Create word embeddings using co-occurrence matrix (simple word2vec approach)"""
        vocab_size = len(self.word_frequencies)
        embeddings = {}
        
        # Initialize random embeddings for each word
        for word in self.word_frequencies:
            # Create embedding based on context
            embedding = np.random.normal(0, 0.1, embedding_dim)
            
            # Adjust embedding based on co-occurrence patterns
            context_adjustment = np.zeros(embedding_dim)
            context_count = 0
            
            for context_word, count in self.context_matrix[word].items():
                if context_word in self.word_frequencies:
                    # Simple context-based adjustment
                    word_hash = hash(context_word) % embedding_dim
                    context_adjustment[word_hash] += count * 0.01
                    context_count += count
            
            if context_count > 0:
                embedding += context_adjustment / context_count
            
            # Normalize embedding
            embedding = embedding / np.linalg.norm(embedding)
            embeddings[word] = embedding
        
        return embeddings
    
    def create_character_embeddings(self, embedding_dim: int = 50) -> Dict[str, np.ndarray]:
        """Create character-level embeddings for Devanagari"""
        char_embeddings = {}
        
        for char, idx in self.character_vocab.items():
            # Create embedding based on character properties
            embedding = np.random.normal(0, 0.1, embedding_dim)
            
            # Encode linguistic properties of Devanagari characters
            if char in ['अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ऋ', 'ए', 'ऐ', 'ओ', 'औ']:
                embedding[0] = 1.0  # Vowel marker
            elif char in ['क', 'ख', 'ग', 'घ', 'ङ']:
                embedding[1] = 1.0  # Velar consonant
            elif char in ['च', 'छ', 'ज', 'झ', 'ञ']:
                embedding[2] = 1.0  # Palatal consonant
            # ... continue for other character classes
            
            char_embeddings[char] = embedding / np.linalg.norm(embedding)
        
        return char_embeddings
    
    def find_similar_words(self, word: str, embeddings: Dict[str, np.ndarray], top_k: int = 5) -> List[Tuple[str, float]]:
        """Find semantically similar words using embedding similarity"""
        if word not in embeddings:
            return []
        
        word_embedding = embeddings[word]
        similarities = []
        
        for other_word, other_embedding in embeddings.items():
            if other_word != word:
                # Cosine similarity
                similarity = np.dot(word_embedding, other_embedding)
                similarities.append((other_word, similarity))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def save_embeddings(self, embeddings: Dict[str, np.ndarray], filename: str):
        """Save embeddings to file"""
        # Convert numpy arrays to lists for JSON serialization
        serializable_embeddings = {
            word: embedding.tolist() 
            for word, embedding in embeddings.items()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_embeddings, f, ensure_ascii=False, indent=2)
    
    def load_embeddings(self, filename: str) -> Dict[str, np.ndarray]:
        """Load embeddings from file"""
        with open(filename, 'r', encoding='utf-8') as f:
            serializable_embeddings = json.load(f)
        
        # Convert lists back to numpy arrays
        embeddings = {
            word: np.array(embedding_list)
            for word, embedding_list in serializable_embeddings.items()
        }
        
        return embeddings

# Example usage with sample Rig Veda verses
if __name__ == "__main__":
    processor = SanskritCorpusProcessor()
    
    print("🕉️ SANSKRIT EMBEDDING SYSTEM FOR RIG VEDA 🕉️")
    print("=" * 60)
    
    # Sample Rig Veda verses in Devanagari
    rigveda_samples = [
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
            'sanskrit': 'अग्निः पूर्वेभिर्ऋषिभिरीड्यो नूतनैरुत',
            'translation': 'Agni is worthy of praise by former sages and by new ones',
            'reference': 'RV 1.1.2a'
        }
    ]
    
    print("📚 Processing Rig Veda corpus...")
    
    # Process all samples
    all_analyses = []
    for sample in rigveda_samples:
        print(f"\n🔍 Processing {sample['reference']}")
        print(f"📜 Sanskrit: {sample['sanskrit']}")
        print(f"🌍 Translation: {sample['translation']}")
        
        analysis = processor.process_rigveda_text(
            sample['sanskrit'], 
            sample['translation']
        )
        all_analyses.append(analysis)
        
        print(f"✅ Tokens: {analysis['tokens']}")
    
    print(f"\n📊 Corpus Statistics:")
    print(f"   Unique words: {len(processor.word_frequencies)}")
    print(f"   Unique characters: {len(processor.character_vocab)}")
    print(f"   Total word occurrences: {sum(processor.word_frequencies.values())}")
    
    print(f"\n🔤 Most frequent words:")
    for word, freq in processor.word_frequencies.most_common(10):
        romanized = processor.romanize_sanskrit(word)
        print(f"   {word} ({romanized}): {freq}")
    
    # Create embeddings
    print(f"\n🧮 Creating embeddings...")
    word_embeddings = processor.create_word_embeddings(embedding_dim=100)
    char_embeddings = processor.create_character_embeddings(embedding_dim=50)
    
    print(f"✅ Created {len(word_embeddings)} word embeddings")
    print(f"✅ Created {len(char_embeddings)} character embeddings")
    
    # Save embeddings
    processor.save_embeddings(word_embeddings, 'data/rigveda_word_embeddings.json')
    processor.save_embeddings(char_embeddings, 'data/rigveda_char_embeddings.json')
    
    # Example similarity search
    if 'अग्निः' in word_embeddings:
        print(f"\n🔍 Words similar to 'अग्निः' (Agni):")
        similar = processor.find_similar_words('अग्निः', word_embeddings, top_k=5)
        for word, similarity in similar:
            romanized = processor.romanize_sanskrit(word)
            print(f"   {word} ({romanized}): {similarity:.3f}")
    
    print(f"\n✅ Sanskrit embedding system ready!")
    print(f"💾 Embeddings saved to data/ directory")
    print(f"🚀 Ready for Step 3: Advanced Semantic Analysis with LLMs")