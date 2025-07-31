"""
Wisdom AI: Spiritual Technology System
Ancient Vedic Knowledge meets Modern AI for Spiritual Seekers

Features:
- Vedic wisdom search and interpretation
- Daily spiritual insights from ancient texts  
- Meditation guidance based on Sanskrit principles
- Karma and dharma analysis tools
- Personalized spiritual learning paths
- Sacred text semantic understanding
"""

import gradio as gr
import json
import random
import datetime
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from collections import defaultdict
import sys

# Import our Sanskrit system
sys.path.append('src')
try:
    from standalone_sanskrit_system import StandaloneSanskritAnalyzer
    print("✅ Sanskrit analyzer loaded for Wisdom AI")
except ImportError as e:
    print(f"❌ Import error: {e}")

@dataclass
class SpiritualInsight:
    """Represents a spiritual insight derived from Vedic texts"""
    sanskrit_source: str
    english_translation: str
    verse_reference: str
    spiritual_principle: str
    practical_application: str
    meditation_focus: str
    daily_practice: str

@dataclass
class WisdomQuery:
    """Represents a user's spiritual question"""
    question: str
    spiritual_domain: str  # dharma, karma, meditation, etc.
    urgency_level: str    # daily, crisis, growth, etc.
    context: str          # life situation

class WisdomAI:
    """
    AI system that provides spiritual guidance using ancient Vedic wisdom
    Applies Rick Briggs' semantic framework to extract timeless insights
    """
    
    def __init__(self):
        self.sanskrit_analyzer = StandaloneSanskritAnalyzer()
        
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
        
        # Initialize Vedic wisdom database
        self._initialize_wisdom_database()
        
        # User interaction tracking
        self.user_sessions = {}
        self.spiritual_journey_data = defaultdict(list)
    
    def _initialize_wisdom_database(self):
        """Initialize comprehensive Vedic wisdom database"""
        
        self.vedic_wisdom = {
            # Fundamental spiritual principles
            'cosmic_order': {
                'sanskrit': 'ऋतं च सत्यं चाभीद्धात्तपसो ऽध्यजायत',
                'translation': 'From cosmic order (rita) and truth (satya) was born from intense spiritual practice (tapas)',
                'reference': 'RV 10.190.1',
                'principle': 'Universal order underlies all existence',
                'application': 'Align your life with natural rhythms and truthful living',
                'meditation': 'Contemplate the order in nature and within yourself',
                'practice': 'Live truthfully and observe natural cycles'
            },
            
            'divine_presence': {
                'sanskrit': 'सर्वं खल्विदं ब्रह्म',
                'translation': 'All this is indeed Brahman (divine consciousness)',
                'reference': 'Chandogya Upanishad 3.14.1',
                'principle': 'Divine consciousness pervades everything',
                'application': 'See the sacred in all beings and situations',
                'meditation': 'Practice seeing unity in diversity',
                'practice': 'Treat all interactions as sacred encounters'
            },
            
            'self_realization': {
                'sanskrit': 'तत्त्वमसि',
                'translation': 'That thou art (You are That)',
                'reference': 'Chandogya Upanishad 6.8.7',
                'principle': 'Your true nature is divine consciousness',  
                'application': 'Recognize your inherent divinity and potential',
                'meditation': 'Inquire into the nature of the self',
                'practice': 'Act from your highest understanding'
            },
            
            'compassionate_action': {
                'sanskrit': 'सर्वे भवन्तु सुखिनः सर्वे सन्तु निरामयाः',
                'translation': 'May all beings be happy, may all beings be free from illness',
                'reference': 'Traditional blessing',
                'principle': 'Universal compassion and well-being',
                'application': 'Extend goodwill to all beings without exception',
                'meditation': 'Send loving-kindness to all beings',
                'practice': 'Include others\' welfare in your daily intentions'
            },
            
            'detached_action': {
                'sanskrit': 'कर्मण्येवाधिकारस्ते मा फलेषु कदाचन',
                'translation': 'You have a right to perform action, but not to the fruits of action',
                'reference': 'Bhagavad Gita 2.47',
                'principle': 'Act without attachment to outcomes',
                'application': 'Do your best work without being attached to results',
                'meditation': 'Contemplate the nature of action and attachment',
                'practice': 'Focus on quality of effort, not results'
            },
            
            'inner_light': {
                'sanskrit': 'ज्योतिर्गमय',
                'translation': 'Lead me from darkness to light',
                'reference': 'Brihadaranyaka Upanishad 1.3.28',
                'principle': 'Movement from ignorance to wisdom',
                'application': 'Actively seek knowledge and understanding',
                'meditation': 'Visualize inner light dispelling darkness',
                'practice': 'Study sacred texts and contemplate their meaning'
            }
        }
        
        # Daily spiritual practices mapped to Sanskrit principles
        self.spiritual_practices = {
            'morning': {
                'sanskrit': 'प्रातः स्मरामि हृदि संस्फुरदात्मतत्त्वम्',
                'practice': 'Morning remembrance of the divine Self',
                'guidance': 'Begin each day with gratitude and intention setting'
            },
            'work': {
                'sanskrit': 'यज्ञार्थात्कर्मणो ऽन्यत्र लोकोऽयं कर्मबन्धनः',
                'practice': 'Transform work into spiritual offering (yajna)',
                'guidance': 'Approach all tasks as sacred service'
            },
            'evening': {
                'sanskrit': 'ॐ शान्तिः शान्तिः शान्तिः',
                'practice': 'Evening peace invocation',
                'guidance': 'End the day with reflection and peace meditation'
            }
        }
    
    def get_daily_wisdom(self, spiritual_focus: str = "general") -> Dict[str, str]:
        """Provide daily spiritual insight based on Vedic wisdom"""
        
        # Select wisdom based on focus area or randomly
        if spiritual_focus == "general" or spiritual_focus not in self.vedic_wisdom:
            wisdom_key = random.choice(list(self.vedic_wisdom.keys()))
        else:
            # Find wisdom related to focus area
            relevant_keys = [key for key in self.vedic_wisdom.keys() 
                           if spiritual_focus.lower() in key.lower()]
            wisdom_key = random.choice(relevant_keys) if relevant_keys else random.choice(list(self.vedic_wisdom.keys()))
        
        wisdom = self.vedic_wisdom[wisdom_key]
        
        today = datetime.date.today()
        
        return {
            'date': today.strftime("%B %d, %Y"),
            'sanskrit': wisdom['sanskrit'],
            'translation': wisdom['translation'], 
            'reference': wisdom['reference'],
            'principle': wisdom['principle'],
            'daily_reflection': wisdom['application'],
            'meditation_guidance': wisdom['meditation'],
            'practice_suggestion': wisdom['practice'],
            'spiritual_theme': wisdom_key.replace('_', ' ').title()
        }
    
    def answer_spiritual_question(self, question: str, life_context: str = "") -> Dict[str, str]:
        """Provide spiritual guidance based on ancient wisdom"""
        
        # Analyze question for spiritual domain
        question_lower = question.lower()
        
        # Identify relevant spiritual domain
        relevant_domain = "wisdom"  # default
        for domain, info in self.spiritual_domains.items():
            if any(concept in question_lower for concept in info['key_concepts']):
                relevant_domain = domain
                break
        
        # Find most relevant wisdom
        relevant_wisdom = []
        for key, wisdom in self.vedic_wisdom.items():
            # Check if wisdom relates to the question
            if (relevant_domain in key or 
                any(word in wisdom['principle'].lower() for word in question_lower.split()) or
                any(word in wisdom['application'].lower() for word in question_lower.split())):
                relevant_wisdom.append((key, wisdom))
        
        # Select best match or random wisdom
        if relevant_wisdom:
            wisdom_key, wisdom = random.choice(relevant_wisdom)
        else:
            wisdom_key = random.choice(list(self.vedic_wisdom.keys()))
            wisdom = self.vedic_wisdom[wisdom_key]
        
        # Create personalized response
        response = {
            'question': question,
            'spiritual_domain': self.spiritual_domains[relevant_domain]['description'],
            'sanskrit_guidance': wisdom['sanskrit'],
            'translation': wisdom['translation'],
            'scriptural_source': wisdom['reference'],
            'wisdom_principle': wisdom['principle'],
            'personal_application': self._personalize_guidance(wisdom['application'], life_context),
            'meditation_practice': wisdom['meditation'],
            'daily_integration': wisdom['practice'],
            'reflection_questions': self._generate_reflection_questions(wisdom_key, question)
        }
        
        return response
    
    def _personalize_guidance(self, general_guidance: str, life_context: str) -> str:
        """Personalize spiritual guidance based on user context"""
        if not life_context:
            return general_guidance
        
        # Simple personalization based on context keywords
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
            ]
        }
        
        return base_questions.get(wisdom_theme, [
            "How does this wisdom apply to my current situation?",
            "What would practicing this teaching look like in my daily life?",
            "How can I embody this understanding more fully?"
        ])
    
    def create_meditation_guidance(self, spiritual_focus: str, duration: int = 20) -> Dict[str, str]:
        """Create personalized meditation guidance based on Vedic principles"""
        
        meditations = {
            'dharma': {
                'sanskrit_mantra': 'ॐ धर्माय नमः',
                'preparation': 'Sit comfortably and reflect on your life purpose',
                'technique': 'Contemplate: "What is my dharma? How can I serve?" Allow insights to arise naturally.',
                'closing': 'Dedicate merit of practice to fulfilling your highest purpose'
            },
            'karma': {
                'sanskrit_mantra': 'ॐ कर्माणि फलानि च',
                'preparation': 'Reflect on recent actions and their consequences',
                'technique': 'Observe the chain of cause and effect in your life without judgment',
                'closing': 'Set intention to act with greater awareness and compassion'
            },
            'peace': {
                'sanskrit_mantra': 'ॐ शान्तिः शान्तिः शान्तिः',
                'preparation': 'Release the day\'s tensions with deep breathing',
                'technique': 'Repeat "Om Shanti" silently, feeling peace in body, mind, and environment',
                'closing': 'Rest in the natural peace that is your true nature'
            },
            'wisdom': {
                'sanskrit_mantra': 'ॐ ज्ञानं ब्रह्म',
                'preparation': 'Bring to mind a question or challenge you\'re facing',
                'technique': 'Ask for wisdom, then listen deeply in silence for inner knowing',
                'closing': 'Trust the wisdom that arises from your deepest Self'
            },
            'compassion': {
                'sanskrit_mantra': 'ॐ मैत्रीं करुणां मुदितां उपेक्षां',
                'preparation': 'Begin with self-compassion for any struggles you face',
                'technique': 'Send loving-kindness to yourself, loved ones, neutral people, difficult people, and all beings',
                'closing': 'Rest in the natural love that connects all beings'
            }
        }
        
        # Select appropriate meditation
        if spiritual_focus not in meditations:
            spiritual_focus = 'peace'  # default
        
        meditation = meditations[spiritual_focus]
        
        # Calculate timing
        prep_time = max(2, duration // 10)
        main_time = duration - prep_time - 3
        closing_time = 3
        
        return {
            'focus': spiritual_focus.title(),
            'duration': f"{duration} minutes",
            'mantra': meditation['sanskrit_mantra'],
            'structure': f"Preparation ({prep_time} min) → Main Practice ({main_time} min) → Closing ({closing_time} min)",
            'preparation': meditation['preparation'], 
            'main_technique': meditation['technique'],
            'closing': meditation['closing'],
            'timer_guidance': f"Set a gentle timer for {duration} minutes, with optional bells at {prep_time} and {duration-closing_time} minutes"
        }
    
    def get_spiritual_learning_path(self, current_level: str, interests: List[str]) -> Dict[str, Any]:
        """Create personalized spiritual learning journey"""
        
        paths = {
            'beginner': {
                'foundation': ['dharma', 'karma', 'meditation'],
                'practices': ['daily_gratitude', 'breath_awareness', 'ethical_living'],
                'texts': ['Bhagavad Gita basics', 'Simple Upanishad verses', 'Yoga Sutras introduction']
            },
            'intermediate': {
                'foundation': ['yoga', 'wisdom', 'compassion'],
                'practices': ['mantra_meditation', 'self_inquiry', 'service'],
                'texts': ['Bhagavad Gita study', 'Upanishads exploration', 'Vedic hymns']
            },
            'advanced': {
                'foundation': ['moksha', 'cosmic_order', 'divine_presence'],
                'practices': ['advanced_meditation', 'scriptural_study', 'teaching_others'],
                'texts': ['Original Sanskrit study', 'Philosophical commentaries', 'Direct experience']
            }
        }
        
        level_data = paths.get(current_level, paths['beginner'])
        
        # Customize based on interests
        recommended_focus = []
        for interest in interests:
            if interest in self.spiritual_domains:
                recommended_focus.append(self.spiritual_domains[interest]['description'])
        
        return {
            'current_level': current_level.title(),
            'recommended_domains': level_data['foundation'],
            'daily_practices': level_data['practices'],
            'study_materials': level_data['texts'],
            'personalized_focus': recommended_focus,
            'next_milestone': 'Deepen understanding through consistent practice and study',
            'weekly_goal': 'Focus on one domain deeply while maintaining daily practices'
        }

def create_wisdom_ai_interface():
    """Create the Wisdom AI spiritual technology interface"""
    
    wisdom_ai = WisdomAI()
    
    # Custom CSS for spiritual aesthetic
    css = """
    .gradio-container {
        font-family: 'Segoe UI', 'Noto Sans', sans-serif;
        background: linear-gradient(135deg, #ffeaa7, #dda0dd, #98d8c8);
    }
    .wisdom-header {
        text-align: center;
        background: linear-gradient(135deg, #ff9a9e, #fad0c4);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .sanskrit-text {
        font-family: 'Noto Sans Devanagari', serif;
        font-size: 20px;
        line-height: 1.8;
        color: #4a4a4a;
    }
    .wisdom-card {
        background: rgba(255,255,255,0.9);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    """
    
    with gr.Blocks(css=css, title="🕉️ Wisdom AI - Spiritual Technology") as app:
        
        # Header
        gr.HTML("""
        <div class="wisdom-header">
            <h1>🕉️ Wisdom AI</h1>
            <h2>Ancient Vedic Wisdom meets Modern Technology</h2>
            <p><em>Spiritual guidance powered by 5000-year-old Sanskrit knowledge</em></p>
            <p><strong>Rick Briggs' Discovery Applied to Spiritual Growth</strong></p>
        </div>
        """)
        
        with gr.Tabs():
            
            # Tab 1: Daily Wisdom
            with gr.Tab("🌅 Daily Wisdom"):
                gr.Markdown("## Receive daily spiritual insights from ancient Vedic texts")
                
                with gr.Row():
                    spiritual_focus = gr.Dropdown(
                        choices=["general", "dharma", "karma", "wisdom", "compassion", "peace"],
                        value="general",
                        label="Spiritual Focus"
                    )
                    get_wisdom_btn = gr.Button("🌟 Get Daily Wisdom", variant="primary")
                
                with gr.Row():
                    with gr.Column():
                        sanskrit_verse = gr.Textbox(
                            label="Sanskrit Wisdom",
                            lines=2,
                            elem_classes=["sanskrit-text"],
                            interactive=False
                        )
                        english_translation = gr.Textbox(
                            label="Translation",
                            lines=2,
                            interactive=False
                        )
                        scriptural_source = gr.Textbox(
                            label="Source",
                            lines=1,
                            interactive=False
                        )
                    
                    with gr.Column():
                        spiritual_principle = gr.Textbox(
                            label="Spiritual Principle",
                            lines=3,
                            interactive=False
                        )
                        daily_reflection = gr.Textbox(
                            label="Daily Reflection",
                            lines=3,
                            interactive=False
                        )
                        practice_suggestion = gr.Textbox(
                            label="Practice Suggestion", 
                            lines=3,
                            interactive=False
                        )
                
                def get_daily_wisdom_handler(focus):
                    wisdom = wisdom_ai.get_daily_wisdom(focus)
                    return (
                        wisdom['sanskrit'],
                        wisdom['translation'],
                        wisdom['reference'],
                        wisdom['principle'],
                        wisdom['daily_reflection'],
                        wisdom['practice_suggestion']
                    )
                
                get_wisdom_btn.click(
                    get_daily_wisdom_handler,
                    inputs=[spiritual_focus],
                    outputs=[sanskrit_verse, english_translation, scriptural_source, 
                            spiritual_principle, daily_reflection, practice_suggestion]
                )
            
            # Tab 2: Spiritual Guidance
            with gr.Tab("🙏 Ask for Guidance"):
                gr.Markdown("## Ask spiritual questions and receive wisdom from ancient texts")
                
                with gr.Row():
                    with gr.Column():
                        spiritual_question = gr.Textbox(
                            label="Your Spiritual Question",
                            placeholder="How can I find my life purpose? How do I deal with difficult emotions? What is the meaning of suffering?",
                            lines=3
                        )
                        life_context = gr.Textbox(
                            label="Life Context (Optional)",
                            placeholder="I'm dealing with career stress, relationship challenges, health issues...",
                            lines=2
                        )
                        ask_guidance_btn = gr.Button("🔮 Seek Guidance", variant="primary")
                    
                    with gr.Column():
                        guidance_output = gr.Markdown(label="Spiritual Guidance")
                
                with gr.Row():
                    reflection_questions = gr.Markdown(label="Reflection Questions")
                
                def get_spiritual_guidance(question, context):
                    if not question.strip():
                        return "Please ask a spiritual question", ""
                    
                    guidance = wisdom_ai.answer_spiritual_question(question, context)
                    
                    output = f"""
## 🕉️ Spiritual Guidance

**Your Question**: {guidance['question']}

**Sanskrit Wisdom**: {guidance['sanskrit_guidance']}
*{guidance['translation']}*
**Source**: {guidance['scriptural_source']}

---

**Spiritual Principle**: {guidance['wisdom_principle']}

**Personal Application**: {guidance['personal_application']}

**Meditation Practice**: {guidance['meditation_practice']}

**Daily Integration**: {guidance['daily_integration']}
                    """
                    
                    reflection = f"""
## 🤔 Questions for Contemplation

{chr(10).join(f"• {q}" for q in guidance['reflection_questions'])}
                    """
                    
                    return output, reflection
                
                ask_guidance_btn.click(
                    get_spiritual_guidance,
                    inputs=[spiritual_question, life_context],
                    outputs=[guidance_output, reflection_questions]
                )
            
            # Tab 3: Meditation Guidance
            with gr.Tab("🧘 Meditation Guidance"):
                gr.Markdown("## Personalized meditation practices based on Vedic traditions")
                
                with gr.Row():
                    with gr.Column():
                        meditation_focus = gr.Dropdown(
                            choices=["peace", "wisdom", "compassion", "dharma", "karma"],
                            value="peace",
                            label="Meditation Focus"
                        )
                        duration = gr.Slider(
                            minimum=5,
                            maximum=60,
                            value=20,
                            step=5,
                            label="Duration (minutes)"
                        )
                        create_meditation_btn = gr.Button("🕉️ Create Meditation", variant="primary")
                    
                    with gr.Column():
                        meditation_guidance = gr.Markdown(label="Meditation Instructions")
                
                def create_meditation_practice(focus, duration_min):
                    guidance = wisdom_ai.create_meditation_guidance(focus, duration_min)
                    
                    output = f"""
# 🧘 {guidance['focus']} Meditation ({guidance['duration']})

**Sanskrit Mantra**: {guidance['mantra']}

## 📝 Structure
{guidance['structure']}

## 🟢 Preparation
{guidance['preparation']}

## 🔵 Main Practice
{guidance['main_technique']}

## 🟡 Closing
{guidance['closing']}

## ⏰ Timer Setup
{guidance['timer_guidance']}

---
*Practice with patience and compassion for yourself*
                    """
                    
                    return output
                
                create_meditation_btn.click(
                    create_meditation_practice,
                    inputs=[meditation_focus, duration],
                    outputs=[meditation_guidance]
                )
            
            # Tab 4: Learning Path
            with gr.Tab("📚 Spiritual Learning"):
                gr.Markdown("## Personalized spiritual development journey")
                
                with gr.Row():
                    with gr.Column():
                        current_level = gr.Dropdown(
                            choices=["beginner", "intermediate", "advanced"],
                            value="beginner",
                            label="Current Level"
                        )
                        interests = gr.CheckboxGroup(
                            choices=["dharma", "karma", "yoga", "meditation", "wisdom", "compassion"],
                            value=["meditation", "wisdom"],
                            label="Areas of Interest"
                        )
                        create_path_btn = gr.Button("🎯 Create Learning Path", variant="primary")
                    
                    with gr.Column():
                        learning_path = gr.Markdown(label="Your Spiritual Learning Journey")
                
                def create_learning_journey(level, interest_list):
                    path = wisdom_ai.get_spiritual_learning_path(level, interest_list)
                    
                    output = f"""
# 🎯 Your Spiritual Learning Path

**Current Level**: {path['current_level']}

## 🎨 Recommended Focus Areas
{chr(10).join(f"• **{domain.replace('_', ' ').title()}**" for domain in path['recommended_domains'])}

## 🔄 Daily Practices
{chr(10).join(f"• {practice.replace('_', ' ').title()}" for practice in path['daily_practices'])}

## 📖 Study Materials
{chr(10).join(f"• {text}" for text in path['study_materials'])}

## 💎 Personalized Recommendations
{chr(10).join(f"• {focus}" for focus in path['personalized_focus'])}

## 🎯 Next Milestone
{path['next_milestone']}

## 📅 This Week's Goal
{path['weekly_goal']}

---
*Remember: Spiritual growth is a journey, not a destination. Be patient and compassionate with yourself.*
                    """
                    
                    return output
                
                create_path_btn.click(
                    create_learning_journey,
                    inputs=[current_level, interests],
                    outputs=[learning_path]
                )
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; margin-top: 30px; padding: 25px; background: linear-gradient(135deg, #a8edea, #fed6e3); border-radius: 15px;">
            <h3>🕉️ Wisdom AI - Where Ancient Meets Modern</h3>
            <p><strong>Powered by Rick Briggs' Discovery</strong></p>
            <p><em>Sanskrit semantic analysis • Vedic wisdom • Spiritual technology</em></p>
            <p>🙏 May all beings find peace, wisdom, and liberation 🙏</p>
        </div>
        """)
    
    return app

# Launch the Wisdom AI interface
if __name__ == "__main__":
    print("🕉️ Launching Wisdom AI - Spiritual Technology System...")
    print("🔮 Ancient Vedic wisdom powered by modern AI")
    
    try:
        app = create_wisdom_ai_interface()
        
        print("✅ Wisdom AI interface created successfully!")
        print("🌟 Features loaded:")
        print("   • Daily spiritual insights from Vedic texts")
        print("   • AI-powered spiritual guidance")
        print("   • Personalized meditation practices")
        print("   • Customized learning paths")
        print("🚀 Launching spiritual technology platform...")
        
        # Launch for Codespaces
        app.launch(
            server_name="0.0.0.0",
            server_port=7861,  # Different port to avoid conflicts
            share=False,
            show_error=True,
            quiet=False
        )
        
    except Exception as e:
        print(f"❌ Error launching Wisdom AI: {e}")
        print("💡 Make sure all dependencies are installed")