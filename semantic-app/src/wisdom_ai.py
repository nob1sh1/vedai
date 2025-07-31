"""
Wisdom AI: Spiritual Technology System
Ancient Vedic Knowledge meets Modern AI for Spiritual Seekers

Features:
- Vedic wisdom search and interpretation using Rig Veda corpus
- AI-powered spiritual guidance from 1,000+ authentic Sanskrit hymns
"""

import gradio as gr
import pickle
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import defaultdict
import sys

# Import Rig Veda processor
sys.path.append('src')
try:
    from rigveda_integration import RigVedaCorpusProcessor, RigVedaHymn
    print("✅ Rig Veda corpus processor loaded for Wisdom AI")
except ImportError as e:
    print(f"❌ Import error for Rig Veda processor: {e}")

# Import Sanskrit analyzer (if available)
try:
    from standalone_sanskrit_system import StandaloneSanskritAnalyzer
    print("✅ Sanskrit analyzer loaded for Wisdom AI")
except ImportError as e:
    print(f"❌ Import error for Sanskrit analyzer: {e}")

@dataclass
class WisdomQuery:
    """Represents a user's spiritual question"""
    question: str
    spiritual_domain: str  # dharma, karma, meditation, etc.
    context: str          # life situation

class WisdomAI:
    """
    AI system that provides spiritual guidance using ancient Vedic wisdom
    Integrates Rig Veda corpus from rigveda_processed_corpus.pkl with semantic search
    """
    
    def __init__(self, corpus_pickle: str = "data/rigveda_processed_corpus.pkl"):
        # Initialize Sanskrit analyzer (if available)
        self.sanskrit_analyzer = None
        try:
            self.sanskrit_analyzer = StandaloneSanskritAnalyzer()
        except:
            pass  # Continue without analyzer if not available
        
        # Load Rig Veda corpus
        self.rigveda_processor = self._load_rigveda_corpus(corpus_pickle)
        
        # Spiritual domains and their Sanskrit foundations
        self.spiritual_domains = {
            'dharma': {
                'sanskrit_term': 'धर्म',
                'description': 'Righteous living, life purpose, moral duty',
                'key_concepts': ['duty', 'righteousness', 'cosmic_order', 'ethics']
            },
            'karma': {
                'sanskrit_term': 'कर्म', 
                'description': 'Action, consequences, spiritual work',
                'key_concepts': ['action', 'consequence', 'work', 'spiritual_practice']
            },
            'moksha': {
                'sanskrit_term': 'मोक्ष',
                'description': 'Liberation, enlightenment, spiritual freedom',
                'key_concepts': ['liberation', 'enlightenment', 'freedom', 'realization']
            },
            'yoga': {
                'sanskrit_term': 'योग',
                'description': 'Union, spiritual practice, integration',
                'key_concepts': ['union', 'practice', 'discipline', 'integration']
            },
            'meditation': {
                'sanskrit_term': 'ध्यान',
                'description': 'Contemplation, focused attention, inner awareness',
                'key_concepts': ['contemplation', 'awareness', 'focus', 'inner_peace']
            },
            'wisdom': {
                'sanskrit_term': 'ज्ञान',
                'description': 'Knowledge, understanding, spiritual insight',
                'key_concepts': ['knowledge', 'insight', 'understanding', 'realization']
            }
        }
        
        # User interaction tracking
        self.user_sessions = {}
        self.spiritual_journey_data = defaultdict(list)
    
    def _load_rigveda_corpus(self, pickle_file: str) -> Optional[RigVedaCorpusProcessor]:
        """Load the processed Rig Veda corpus from rigveda_processed_corpus.pkl"""
        try:
            processor = RigVedaCorpusProcessor()
            with open(pickle_file, 'rb') as f:
                corpus_data = pickle.load(f)
            processor.hymns = [
                RigVedaHymn(
                    book=d['book'],
                    hymn=d['hymn'],
                    reference=d['reference'],
                    sanskrit=d['sanskrit'],
                    romanized=d['romanized'],
                    verses=d['verses'],
                    url=d['url'],
                    spiritual_themes=d['spiritual_themes'],
                    deity_focus=d['deity_focus'],
                    ritual_context=d['ritual_context'],
                    philosophical_concepts=d['philosophical_concepts'],
                    embedding=np.array(d['embedding']) if d['embedding'] else None
                ) for d in corpus_data
            ]
            print(f"✅ Loaded {len(processor.hymns)} hymns from {pickle_file}")
            return processor
        except Exception as e:
            print(f"❌ Error loading Rig Veda corpus from {pickle_file}: {e}")
            return None
    
    def answer_spiritual_question(self, question: str, life_context: str = "") -> Dict[str, str]:
        """Provide spiritual guidance using Rig Veda corpus from rigveda_processed_corpus.pkl"""
        if not question.strip():
            return {
                'question': question,
                'spiritual_domain': 'None',
                'sanskrit_guidance': '',
                'translation': '',
                'scriptural_source': '',
                'wisdom_principle': 'Please ask a spiritual question',
                'personal_application': '',
                'meditation_practice': '',
                'daily_integration': '',
                'reflection_questions': []
            }
        
        # Identify relevant spiritual domain
        question_lower = question.lower()
        relevant_domain = "wisdom"
        for domain, info in self.spiritual_domains.items():
            if any(concept in question_lower for concept in info['key_concepts']):
                relevant_domain = domain
                break
        
        # Use Rig Veda corpus
        if self.rigveda_processor and self.rigveda_processor.hymns:
            # Map spiritual domain to Rig Veda theme
            theme_mapping = {
                'dharma': 'cosmic_order',
                'karma': 'sacrifice',
                'moksha': 'wisdom',
                'yoga': 'prayer',
                'meditation': 'prayer',
                'wisdom': 'wisdom'
            }
            rigveda_theme = theme_mapping.get(relevant_domain, 'cosmic_order')
            
            # Search corpus for relevant hymns
            results = self.rigveda_processor.search_corpus(question, top_k=3)
            if results:
                hymn, score = results[0]  # Take top result
                principle = f"Guidance inspired by {hymn.deity_focus.title()} and {rigveda_theme.replace('_', ' ').title()}"
                application = f"Apply the essence of {hymn.deity_focus.title()}'s teachings to your situation."
                meditation = f"Meditate on {rigveda_theme.replace('_', ' ').title()} to find clarity."
                practice = f"Integrate {rigveda_theme.replace('_', ' ').title()} into your daily actions."
                
                return {
                    'question': question,
                    'spiritual_domain': self.spiritual_domains[relevant_domain]['description'],
                    'sanskrit_guidance': hymn.sanskrit[:200],
                    'translation': hymn.romanized[:200],  # Use romanized as proxy
                    'scriptural_source': hymn.reference,
                    'wisdom_principle': principle,
                    'personal_application': self._personalize_guidance(application, life_context),
                    'meditation_practice': meditation,
                    'daily_integration': practice,
                    'reflection_questions': self._generate_reflection_questions(rigveda_theme, question)
                }
        
        # Return error if corpus is unavailable
        return {
            'question': question,
            'spiritual_domain': 'None',
            'sanskrit_guidance': '',
            'translation': '',
            'scriptural_source': '',
            'wisdom_principle': 'Error: Rig Veda corpus unavailable. Please ensure data/rigveda_processed_corpus.pkl is accessible.',
            'personal_application': '',
            'meditation_practice': '',
            'daily_integration': '',
            'reflection_questions': []
        }
    
    def _personalize_guidance(self, general_guidance: str, life_context: str) -> str:
        """Personalize spiritual guidance based on user context"""
        if not life_context:
            return general_guidance
        
        context_lower = life_context.lower()
        personalized = general_guidance
        
        if "work" in context_lower or "career" in context_lower:
            personalized += " In your professional life, this means bringing integrity and purpose to your work."
        if "relationship" in context_lower or "family" in context_lower:
            personalized += " In relationships, practice patience, understanding, and unconditional love."
        if "health" in context_lower or "illness" in context_lower:
            personalized += " For physical well-being, remember that health encompasses body, mind, and spirit."
        if "stress" in context_lower or "anxiety" in context_lower:
            personalized += " When facing stress, return to your breath and remember that this too shall pass."
        
        return personalized
    
    def _generate_reflection_questions(self, wisdom_theme: str, user_question: str) -> List[str]:
        """Generate contemplative questions based on wisdom theme"""
        base_questions = {
            'cosmic_order': [
                "How can I better align my daily actions with natural rhythms?",
                "What patterns do I notice in my life that reflect universal order?",
                "Where am I fighting against the natural flow, and how can I surrender?"
            ],
            'divine_presence': [
                "In what moments today did I experience the sacred?",
                "How can I cultivate awareness of divinity in ordinary activities?",
                "What would change if I truly saw everyone as divine?"
            ],
            'self_realization': [
                "What is my truest nature beyond roles and identities?",
                "How do my actions reflect my highest understanding of myself?",
                "What beliefs about myself are ready to be released?"
            ],
            'compassionate_action': [
                "How can I extend more kindness to myself and others?",
                "What would love do in this situation?",
                "How does my well-being connect to the well-being of all?"
            ],
            'detached_action': [
                "Where am I attached to specific outcomes?",
                "How can I give my best effort without attachment?",
                "What would I do if I knew I couldn't fail?"
            ],
            'inner_light': [
                "What knowledge am I seeking, and why?",
                "How can I be a source of light for others?",
                "What darkness in my life is ready for illumination?"
            ],
            'agni': [
                "How can I cultivate my inner fire for transformation?",
                "What needs purification in my life?",
                "How can I connect with the divine through intention?"
            ],
            'indra': [
                "Where can I find strength to overcome obstacles?",
                "How can I embody courage in my current challenges?",
                "What victories can I celebrate in my spiritual journey?"
            ],
            'soma': [
                "How can I access inner joy and bliss?",
                "What practices elevate my consciousness?",
                "How can I connect with the divine nectar of life?"
            ],
            'surya': [
                "How can I bring light to my decisions and actions?",
                "What areas of my life need illumination?",
                "How can I cultivate awareness of the divine light within?"
            ],
            'varuna': [
                "How can I align with truth and justice in my actions?",
                "What moral principles guide my decisions?",
                "How can I honor the cosmic order in my life?"
            ],
            'vayu': [
                "How can I connect with my inner life force?",
                "What practices energize my body and mind?",
                "How can I flow with the winds of change?"
            ],
            'sacrifice': [
                "What can I offer to my higher purpose?",
                "How can I transform my actions into sacred offerings?",
                "What sacrifices am I willing to make for growth?"
            ],
            'prayer': [
                "How can I deepen my connection to the divine?",
                "What intentions can I set through prayer?",
                "How can I make my life a living prayer?"
            ],
            'creation': [
                "What am I creating in my life right now?",
                "How can I align my creations with divine will?",
                "What new beginnings are emerging in my journey?"
            ]
        }
        
        return base_questions.get(wisdom_theme, [
            "How does this wisdom apply to my current situation?",
            "What would practicing this teaching look like in my daily life?",
            "How can I embody this understanding more fully?"
        ])

def create_wisdom_ai_interface():
    """Create a simple Wisdom AI interface for spiritual questions"""
    wisdom_ai = WisdomAI(corpus_pickle="data/rigveda_processed_corpus.pkl")
    
    # Minimal CSS for a clean, simple design
    css = """
    .gradio-container {
        font-family: 'Arial', sans-serif;
        background: #f5f5f5;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    .sanskrit-text {
        font-family: 'Noto Sans Devanagari', serif;
        font-size: 18px;
        color: #333;
    }
    .output-box {
        background: #fff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    """
    
    with gr.Blocks(css=css, title="Wisdom AI - Spiritual Guidance") as app:
        gr.Markdown(
            """
            # 🕉️ Wisdom AI
            Ask a spiritual question and receive guidance from the Rig Veda
            """,
            elem_classes=["wisdom-header"]
        )
        
        # Input dialog box
        spiritual_question = gr.Textbox(
            label="Your Spiritual Question",
            placeholder="How can I find inner peace? What is my life purpose?",
            lines=3
        )
        
        # Submit button
        submit_btn = gr.Button("Submit", variant="primary")
        
        # Output area
        guidance_output = gr.Markdown(
            label="Spiritual Guidance",
            elem_classes=["output-box"]
        )
        
        def get_spiritual_guidance(question):
            guidance = wisdom_ai.answer_spiritual_question(question)
            
            output = f"""
### 🕉️ Spiritual Guidance

**Your Question**: {guidance['question']}

**Sanskrit Wisdom**: {guidance['sanskrit_guidance']}  
*{guidance['translation']}*  
**Source**: {guidance['scriptural_source']}

**Spiritual Principle**: {guidance['wisdom_principle']}

**Personal Application**: {guidance['personal_application']}

**Meditation Practice**: {guidance['meditation_practice']}

**Daily Integration**: {guidance['daily_integration']}

**Questions for Contemplation**:  
{chr(10).join(f"- {q}" for q in guidance['reflection_questions'])}
            """
            return output
        
        submit_btn.click(
            get_spiritual_guidance,
            inputs=[spiritual_question],
            outputs=[guidance_output]
        )
    
    return app

if __name__ == "__main__":
    print("🕉️ Launching Wisdom AI - Spiritual Technology System...")
    print("🔮 Ancient Vedic wisdom powered by modern AI")
    
    try:
        app = create_wisdom_ai_interface()
        
        print("✅ Wisdom AI interface created successfully!")
        print("🌟 Feature loaded: AI-powered spiritual guidance from Rig Veda")
        print("🚀 Launching spiritual technology platform...")
        
        # Launch for GitHub Codespaces
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,  # Standard port for Codespaces
            share=False,      # No public sharing in Codespaces
            show_error=True,
            quiet=False
        )
        
    except Exception as e:
        print(f"❌ Error launching Wisdom AI: {e}")
        print("💡 Make sure all dependencies are installed: gradio, sentence-transformers, numpy")