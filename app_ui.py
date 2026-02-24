import streamlit as st
import os

# --- Page Config ---
st.set_page_config(
    page_title="Webnovel Architect",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar Navigation ---
with st.sidebar:
    st.title("📖 Webnovel Architect")
    st.caption("Neuro-Symbolic Story Intelligence")
    st.divider()
    
    # Navigation Radio
    page = st.radio(
        "Navigation",
        ["Dashboard", "Ingestion Engine", "Wiki Memory", "Knowledge Graph", "Audio Hub"]
    )
    
    st.divider()
    st.info("System Status: **Online**")

# --- Page Router ---
if page == "Dashboard":
    st.header("Dashboard Metrics")
    st.markdown("Welcome to Webnovel Architect. Use the sidebar to navigate.")
    
    # Load config and runtime DB
    from app.services.ingest import _runtime_db, _chapter_counter
    import yaml
    
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    col1, col2, col3 = st.columns(3)
    col1.metric("Processed Chapters", _chapter_counter)
    col2.metric("Discovered Characters", len(_runtime_db))
    col3.metric("Graduated Characters", len([c for c in _runtime_db.values() if c.voice_id is not None]))
    
    st.subheader("System Configuration")
    st.code(f"LLM Engine: {config.get('llm_model')}\nMain TTS: {config.get('tts_engine')}\nFallback TTS: {config.get('fallback_tts')}", language="yaml")
    
elif page == "Ingestion Engine":
    st.header("Ingestion Engine")
    st.markdown("Paste new chapter text here to parse Dialogue and Events into the Knowledge Graph.")
    
    chapter_title = st.text_input("Chapter Title", placeholder="e.g., Chapter 1: The Beginning")
    chapter_text = st.text_area("Chapter Text", height=300)
    
    if st.button("Process Chapter", type="primary"):
        if not chapter_title or not chapter_text:
            st.error("Please provide both a title and chapter text.")
        else:
            with st.spinner("Processing semantics and extracting events..."):
                from app.services.ingest import ingest_chapter
                try:
                    chapter = ingest_chapter(chapter_title, chapter_text)
                    st.success(f"Successfully processed {chapter_title}!")
                    
                    # Display Extracted Events
                    st.subheader("Extracted Data")
                    st.json({
                        "id": chapter.id,
                        "title": chapter.title,
                        # Assuming chapter model doesn't store the raw response, we just show success.
                        # Real app would display the DyG-RAG delta here.
                        "status": "Graph Updated"
                    })
                except Exception as e:
                    st.error(f"Error processing chapter: {str(e)}")

elif page == "Wiki Memory":
    st.header("Character Wiki (Memory)")
    st.markdown("Browse the generated characters and their canonical status.")
    
    import os
    wiki_dir = "wiki"
    
    if os.path.exists(wiki_dir):
        files = [f for f in os.listdir(wiki_dir) if f.endswith('.md')]
        if not files:
            st.info("No characters in Wiki yet. Process some chapters first!")
        else:
            selected_file = st.selectbox("Select Character", files)
            with open(os.path.join(wiki_dir, selected_file), "r") as f:
                content = f.read()
            st.markdown("---")
            st.markdown(content)
    else:
        st.warning(f"Wiki directory '{wiki_dir}' does not exist.")
    
elif page == "Audio Hub":
    st.header("Audio Hub")
    st.markdown("Generate and test audio for graduated characters.")
    
    from app.services.ingest import _runtime_db
    import yaml
    import asyncio
    
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    graduated_chars = [c for c in _runtime_db.values() if c.voice_id is not None]
    
    if not graduated_chars:
        st.info("No characters have graduated to the Main Cast yet. Process more chapters to trigger graduation!")
    else:
        char_options = {c.character_id: c for c in graduated_chars}
        selected_id = st.selectbox("Select Character", list(char_options.keys()), format_func=lambda x: f"{x} (Voice: {char_options[x].voice_id})")
        
        test_text = st.text_area("Dialogue to Speak", "Hello world, this is my voice.")
        
        engine_type = st.radio("TTS Engine", [config.get('tts_engine'), config.get('fallback_tts')], horizontal=True)
        
        if st.button("Generate Audio"):
            with st.spinner(f"Synthesizing using {engine_type}..."):
                from adapters.tts_adapter import get_tts_engine
                tts = get_tts_engine(engine_type)
                
                char = char_options[selected_id]
                voice = char.voice_id
                
                import os
                if not os.path.exists("output"): os.makedirs("output")
                filename = f"output/ui_test_{char.character_id}.wav"
                
                try:
                    if asyncio.iscoroutinefunction(tts.generate_audio):
                        asyncio.run(tts.generate_audio(test_text, voice, filename))
                    else:
                        tts.generate_audio(test_text, voice, filename)
                        
                    st.success("Audio generated!")
                    st.audio(filename)
                except Exception as e:
                    st.error(f"Failed to generate audio: {str(e)}")
elif page == "Knowledge Graph":
    st.header("Knowledge Graph")
    st.markdown("Interactive visualization of the character relationship graph built from ingested chapters.")
    
    from adapters.graph_adapter import get_graph_engine
    from pyvis.network import Network
    import streamlit.components.v1 as components
    import tempfile
    
    graph_engine = get_graph_engine()
    G = graph_engine.graph
    
    if len(G.nodes) == 0:
        st.info("The knowledge graph is empty. Process some chapters first!")
    else:
        # Build pyvis network
        net = Network(
            height="600px",
            width="100%",
            bgcolor="#1a1a2e",
            font_color="white",
            directed=True
        )
        net.toggle_physics(True)
        
        # Add nodes with color coding
        for node, data in G.nodes(data=True):
            node_type = data.get("type", "unknown")
            if node_type == "character":
                color = "#e94560"  # red for characters
                size  = 25
            else:
                color = "#0f3460"  # blue for events
                size  = 15
            net.add_node(str(node), label=str(node), color=color, size=size, title=f"Type: {node_type}")
        
        # Add edges
        for src, dst, data in G.edges(data=True):
            relation = data.get("relation", "")
            net.add_edge(str(src), str(dst), title=relation, color="#888")
        
        # Save to temp HTML and embed
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w") as f:
            net.save_graph(f.name)
            html_path = f.name
        
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        components.html(html_content, height=620, scrolling=False)
        
        # Stats below
        col1, col2 = st.columns(2)
        char_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "character"]
        event_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "event"]
        col1.metric("Character Nodes", len(char_nodes))
        col2.metric("Event Nodes", len(event_nodes))

