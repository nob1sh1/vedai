"""
Step 4: Interactive Web Interface for Vedic Sanskrit Analysis
Beautiful Gradio interface for exploring Rig Veda using Rick Briggs' framework

Features:
- Real-time Sanskrit text analysis
- Interactive knowledge graph exploration
- Semantic search through Vedic corpus
- Visual representation of karaka relations
- Educational interface for Sanskrit learning
"""

import gradio as gr
import json
import sys
import os
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd

# Import our standalone system
sys.path.append('src')
try:
    from standalone_sanskrit_system import StandaloneSanskritAnalyzer
    print("✅ Successfully imported Sanskrit analyzer")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure standalone_sanskrit_system.py is in the src/ directory")

class VedicWebInterface:
    """Web interface for Vedic Sanskrit analysis"""
    
    def __init__(self):
        self.analyzer = StandaloneSanskritAnalyzer()
        self.knowledge_graph = {}
        self.corpus_analyses = []
        
        # Pre-load some Rig Veda verses for demonstration
        self.sample_corpus = [
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
            },
            {
                'sanskrit': 'स देवाँ एह वक्षति',
                'translation': 'He will bring the gods here',
                'reference': 'RV 1.1.2b'
            },
            {
                'sanskrit': 'इन्द्रं मित्रं वरुणमग्निमाहुः',
                'translation': 'They call him Indra, Mitra, Varuna, Agni',
                'reference': 'RV 1.164.46a'
            }
        ]
        
        # Initialize with sample corpus
        self._initialize_corpus()
    
    def _initialize_corpus(self):
        """Initialize the corpus with sample verses"""
        print("🔄 Initializing Vedic corpus...")
        
        for verse in self.sample_corpus:
            analysis = self.analyzer.analyze_rigveda_verse(
                verse['sanskrit'],
                verse['translation'],
                verse['reference']
            )
            self.corpus_analyses.append(analysis)
        
        # Build knowledge graph
        self.knowledge_graph = self.analyzer.build_knowledge_graph(self.corpus_analyses)
        print(f"✅ Corpus initialized with {len(self.corpus_analyses)} verses")
    
    def analyze_sanskrit_text(self, sanskrit_input: str, translation_input: str = "") -> Tuple[str, str, str]:
        """Analyze user-provided Sanskrit text"""
        if not sanskrit_input.strip():
            return "❌ Please enter Sanskrit text to analyze", "", ""
        
        try:
            # Analyze the text
            analysis = self.analyzer.analyze_rigveda_verse(
                sanskrit_input.strip(),
                translation_input.strip(),
                "User Input"
            )
            
            # Format detailed analysis
            detailed_output = self.analyzer.visualize_analysis(analysis)
            
            # Create semantic triples table
            triples_data = []
            for triple in analysis['triples']:
                karaka_meaning = self.analyzer.karaka_relations.get(triple.karaka, triple.karaka)
                triples_data.append([
                    triple.verb_root,
                    triple.karaka,
                    karaka_meaning,
                    triple.word,
                    triple.meaning or "Unknown",
                    f"{triple.confidence:.2f}"
                ])
            
            # Create summary
            summary = f"""
## Analysis Summary
- **Semantic Field**: {analysis['semantic_field']}
- **Romanized**: {analysis['romanized']}
- **Relations Found**: {len(analysis['triples'])}
- **Entities Recognized**: {analysis['entities_found']}
- **Confidence**: {analysis['confidence']:.2f}
            """
            
            return detailed_output, summary, triples_data
            
        except Exception as e:
            return f"❌ Analysis error: {str(e)}", "", []
    
    def search_vedic_corpus(self, query: str) -> Tuple[str, List]:
        """Search the Vedic corpus"""
        if not query.strip():
            return "❌ Please enter a search query", []
        
        try:
            results = self.analyzer.query_knowledge_graph(query.strip(), self.knowledge_graph)
            
            if not results:
                return f"No results found for '{query}'", []
            
            # Format results
            output = f"🔍 **Search Results for '{query}'** ({len(results)} found)\n\n"
            
            results_data = []
            for i, result in enumerate(results[:10], 1):
                rel = result['relationship']
                
                output += f"**{i}. {rel['verse']}**\n"
                output += f"   - Entity: {rel['entity']} ({rel['relation']})\n"
                output += f"   - Verb: {rel['verb']}\n"
                output += f"   - Score: {result['score']:.1f}\n\n"
                
                results_data.append([
                    rel['verse'],
                    rel['entity'],
                    rel['relation'],
                    rel['verb'],
                    f"{result['score']:.1f}"
                ])
            
            return output, results_data
            
        except Exception as e:
            return f"❌ Search error: {str(e)}", []
    
    def explore_entity(self, entity_name: str) -> str:
        """Explore a specific Vedic entity"""
        if not entity_name.strip():
            return "❌ Please enter an entity name"
        
        entity_name = entity_name.strip()
        
        # Check if entity exists in knowledge graph
        entities = self.knowledge_graph.get('entities', {})
        
        if entity_name in entities:
            entity_info = entities[entity_name]
            
            output = f"# 🕉️ Entity: {entity_name}\n\n"
            output += f"**Domain**: {entity_info['domain']}\n"
            output += f"**Appears in verses**: {', '.join(entity_info['verses'])}\n"
            output += f"**Relations**: {', '.join(set(entity_info['relations']))}\n\n"
            
            # Add vocabulary information if available
            if entity_name in self.analyzer.vedic_vocabulary:
                vocab_info = self.analyzer.vedic_vocabulary[entity_name]
                output += f"**Meaning**: {vocab_info['meaning']}\n"
                output += f"**Semantic Domain**: {vocab_info['domain']}\n"
            
            return output
        else:
            # Search for similar entities
            similar = [name for name in entities.keys() if entity_name.lower() in name.lower() or name.lower() in entity_name.lower()]
            
            if similar:
                output = f"Entity '{entity_name}' not found exactly. Similar entities:\n\n"
                for sim in similar[:5]:
                    output += f"- {sim}\n"
                return output
            else:
                return f"❌ Entity '{entity_name}' not found in corpus"
    
    def get_corpus_statistics(self) -> Tuple[str, List]:
        """Get statistics about the corpus"""
        stats = f"""
# 📊 Corpus Statistics

## Overview
- **Total verses analyzed**: {len(self.corpus_analyses)}
- **Unique entities**: {len(self.knowledge_graph.get('entities', {}))}
- **Total relationships**: {len(self.knowledge_graph.get('relationships', []))}
- **Semantic domains**: {len(self.knowledge_graph.get('domains', {}))}

## Vocabulary Coverage
- **Vedic terms in database**: {len(self.analyzer.vedic_vocabulary)}
- **Verb roots known**: {len(self.analyzer.verb_roots)}
- **Karaka relations**: {len(self.analyzer.karaka_relations)}

## Semantic Domains
        """
        
        domains = self.knowledge_graph.get('domains', {})
        for domain, verses in domains.items():
            stats += f"- **{domain}**: {len(verses)} verses\n"
        
        # Create entities table
        entities_data = []
        entities = self.knowledge_graph.get('entities', {})
        for entity, info in list(entities.items())[:20]:  # Top 20 entities
            entities_data.append([
                entity,
                info['domain'],
                len(info['verses']),
                ', '.join(info['verses'][:3]) + ('...' if len(info['verses']) > 3 else '')
            ])
        
        return stats, entities_data
    
    def show_karaka_system(self) -> str:
        """Show the Paninian karaka system"""
        output = """
# 📚 Paninian Karaka System
## The Seven Case Relations (Rick Briggs' Framework)

The ancient Sanskrit grammarians developed a sophisticated system for analyzing semantic roles, which Rick Briggs showed is identical to modern AI semantic networks.

        """
        
        for karaka, meaning in self.analyzer.karaka_relations.items():
            output += f"### {karaka}\n"
            output += f"**Meaning**: {meaning}\n\n"
            
            # Add examples from corpus
            examples = []
            for analysis in self.corpus_analyses:
                for triple in analysis['triples']:
                    if triple.karaka == karaka:
                        examples.append(f"{triple.word} in {analysis['reference']}")
                        if len(examples) >= 2:
                            break
                if len(examples) >= 2:
                    break
            
            if examples:
                output += f"**Examples**: {', '.join(examples)}\n\n"
            else:
                output += "\n"
        
        output += """
---
*This system, developed over 1000 years ago, produces the same semantic analysis as modern AI systems!*
        """
        
        return output

def create_vedic_interface():
    """Create the Gradio interface"""
    
    # Initialize the interface
    interface = VedicWebInterface()
    
    # Custom CSS for styling
    css = """
    .gradio-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .vedic-header {
        text-align: center;
        background: linear-gradient(135deg, #ff9933, #ffffff, #138808);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .sanskrit-text {
        font-family: 'Noto Sans Devanagari', serif;
        font-size: 18px;
        line-height: 1.6;
    }
    """
    
    with gr.Blocks(css=css, title="🕉️ Vedic Sanskrit Analyzer") as app:
        
        # Header
        gr.HTML("""
        <div class="vedic-header">
            <h1>🕉️ Vedic Sanskrit Analyzer</h1>
            <h3>Based on Rick Briggs' 1985 Research</h3>
            <p><em>Ancient Sanskrit Grammar meets Modern AI</em></p>
        </div>
        """)
        
        with gr.Tabs():
            
            # Tab 1: Text Analysis
            with gr.Tab("📝 Analyze Sanskrit Text"):
                gr.Markdown("## Enter Sanskrit text for semantic analysis")
                
                with gr.Row():
                    with gr.Column():
                        sanskrit_input = gr.Textbox(
                            label="Sanskrit Text (Devanagari)",
                            placeholder="अग्निमीळे पुरोहितम्...",
                            lines=3,
                            elem_classes=["sanskrit-text"]
                        )
                        translation_input = gr.Textbox(
                            label="Translation (Optional)",
                            placeholder="I praise Agni...",
                            lines=2
                        )
                        analyze_btn = gr.Button("🔍 Analyze Text", variant="primary")
                    
                    with gr.Column():
                        analysis_output = gr.Textbox(
                            label="Detailed Analysis",
                            lines=15,
                            show_copy_button=True
                        )
                
                with gr.Row():
                    summary_output = gr.Markdown(label="Summary")
                
                with gr.Row():
                    triples_table = gr.Dataframe(
                        headers=["Verb Root", "Karaka", "Relation Meaning", "Word", "Meaning", "Confidence"],
                        label="Semantic Triples"
                    )
                
                analyze_btn.click(
                    interface.analyze_sanskrit_text,
                    inputs=[sanskrit_input, translation_input],
                    outputs=[analysis_output, summary_output, triples_table]
                )
            
            # Tab 2: Corpus Search
            with gr.Tab("🔍 Search Vedic Corpus"):
                gr.Markdown("## Search through analyzed Rig Veda verses")
                
                with gr.Row():
                    search_input = gr.Textbox(
                        label="Search Query",
                        placeholder="agni fire ritual, indra storm, sacrifice...",
                        lines=1
                    )
                    search_btn = gr.Button("🔍 Search", variant="primary")
                
                with gr.Row():
                    search_results = gr.Markdown(label="Search Results")
                
                with gr.Row():
                    results_table = gr.Dataframe(
                        headers=["Verse", "Entity", "Relation", "Verb", "Score"],
                        label="Detailed Results"
                    )
                
                search_btn.click(
                    interface.search_vedic_corpus,
                    inputs=[search_input],
                    outputs=[search_results, results_table]
                )
            
            # Tab 3: Entity Explorer
            with gr.Tab("🏛️ Explore Entities"):
                gr.Markdown("## Explore Vedic concepts and deities")
                
                with gr.Row():
                    entity_input = gr.Textbox(
                        label="Entity Name",
                        placeholder="अग्नि, इन्द्र, यज्ञ...",
                        lines=1
                    )
                    explore_btn = gr.Button("🔍 Explore", variant="primary")
                
                with gr.Row():
                    entity_output = gr.Markdown(label="Entity Information")
                
                explore_btn.click(
                    interface.explore_entity,
                    inputs=[entity_input],
                    outputs=[entity_output]
                )
            
            # Tab 4: Corpus Statistics
            with gr.Tab("📊 Corpus Statistics"):
                gr.Markdown("## Overview of the analyzed corpus")
                
                stats_btn = gr.Button("📊 Load Statistics", variant="primary") 
                
                with gr.Row():
                    stats_output = gr.Markdown(label="Statistics")
                
                with gr.Row():
                    entities_table = gr.Dataframe(
                        headers=["Entity", "Domain", "Verse Count", "Appears In"],
                        label="Top Entities"
                    )
                
                stats_btn.click(
                    interface.get_corpus_statistics,
                    outputs=[stats_output, entities_table]
                )
            
            # Tab 5: Learn Karaka System
            with gr.Tab("📚 Karaka System"):
                gr.Markdown("## Learn about Paninian Grammar")
                
                karaka_btn = gr.Button("📚 Show Karaka System", variant="primary")
                karaka_output = gr.Markdown(label="Karaka System Explanation")
                
                karaka_btn.click(
                    interface.show_karaka_system,
                    outputs=[karaka_output]
                )
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; margin-top: 30px; padding: 20px; background-color: #f0f0f0; border-radius: 10px;">
            <p><strong>🕉️ Vedic Sanskrit Analyzer</strong></p>
            <p>Implementing Rick Briggs' 1985 discovery that Sanskrit grammar = Modern AI semantic networks</p>
            <p><em>No external APIs required • Pure computational linguistics</em></p>
        </div>
        """)
    
    return app

# Launch the interface
if __name__ == "__main__":
    print("🚀 Starting Vedic Sanskrit Web Interface...")
    
    try:
        app = create_vedic_interface()
        
        print("✅ Interface created successfully!")
        print("🌐 Launching web interface...")
        print("📝 You can now analyze Sanskrit text through the web UI!")
        
        # Launch with specific settings for Codespaces
        app.launch(
            server_name="0.0.0.0",  # Allow external access
            server_port=7860,       # Standard Gradio port
            share=False,            # Don't create public link
            show_error=True,        # Show errors in interface
            quiet=False             # Show startup messages
        )
        
    except Exception as e:
        print(f"❌ Error launching interface: {e}")
        print("💡 Make sure Gradio is installed and the standalone system is working")
        