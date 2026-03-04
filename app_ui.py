import streamlit as st
import os

# Load .env manually to ensure API keys are available
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip().strip('"\''))

# --- Page Config ---
st.set_page_config(
    page_title="Webnovel Architect",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar Navigation ---
from app.core.story_manager import StoryManager

# Initialize StoryManager State
if 'active_story_uuid' not in st.session_state:
    st.session_state['active_story_uuid'] = None

with st.sidebar:
    st.title("📖 Webnovel Architect")
    st.caption("Neuro-Symbolic Story Intelligence")
    st.divider()
    
    # Story Management UI
    st.subheader("📚 Story Manager")
    stories = StoryManager.list_stories()
    
    if not stories:
        st.warning("No stories found. Create one!")
        
    story_options = {s['uuid']: s['name'] for s in stories}
    
    # Selection
    if stories:
        # Default to the first story if none selected or if selected was deleted
        if st.session_state['active_story_uuid'] not in story_options:
            st.session_state['active_story_uuid'] = stories[0]['uuid']
            
        selected_uuid = st.selectbox(
            "Active Story",
            options=list(story_options.keys()),
            format_func=lambda x: story_options[x],
            index=list(story_options.keys()).index(st.session_state['active_story_uuid']) if st.session_state['active_story_uuid'] in story_options else 0
        )
        st.session_state['active_story_uuid'] = selected_uuid
    
    # Create New Story
    with st.expander("➕ New Story"):
        with st.form("new_story_form"):
            new_name = st.text_input("Story Name")
            if st.form_submit_button("Create") and new_name:
                new_uuid = StoryManager.create_story(new_name)
                st.session_state['active_story_uuid'] = new_uuid
                st.rerun()
                
    # Manage Current Story
    if st.session_state['active_story_uuid']:
        with st.expander("⚙️ Manage Story"):
            cur_uuid = st.session_state['active_story_uuid']
            
            with st.form("rename_form"):
                rename_name = st.text_input("New Name", value=story_options.get(cur_uuid, ""))
                if st.form_submit_button("Rename") and rename_name:
                    StoryManager.rename_story(cur_uuid, rename_name)
                    st.rerun()
                    
            if st.button("Copy Story", use_container_width=True):
                new_uuid = StoryManager.duplicate_story(cur_uuid)
                st.session_state['active_story_uuid'] = new_uuid
                st.rerun()
                
            if st.button("🗑️ Delete Story", type="primary", use_container_width=True):
                StoryManager.soft_delete_story(cur_uuid)
                st.session_state['active_story_uuid'] = None
                st.rerun()

    st.divider()
    
    # Navigation Radio
    page = st.radio(
        "Navigation",
        ["Dashboard", "Ingestion Engine", "Wiki Memory", "Knowledge Graph", "Audio Hub"]
    )
    
    st.divider()
    st.info("System Status: **Online**")
    
# Stop execution if no story is active
if not st.session_state['active_story_uuid']:
    st.info("👈 Please create or select a story from the sidebar to continue.")
    st.stop()
    
active_story_uuid = st.session_state['active_story_uuid']

# --- Page Router ---
if page == "Dashboard":
    st.header("Dashboard Metrics")
    st.markdown("Welcome to Webnovel Architect. Use the sidebar to navigate.")
    
    import yaml
    from app.services.ingest import load_runtime
    
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    chapter_counter, runtime_db = load_runtime(active_story_uuid)
        
    col1, col2, col3 = st.columns(3)
    col1.metric("Processed Chapters", chapter_counter)
    col2.metric("Discovered Characters", len(runtime_db))
    col3.metric("Graduated Characters", len([c for c in runtime_db.values() if c.voice_id is not None]))
    
    st.subheader("System Configuration")
    st.code(f"LLM Engine: {config.get('llm_model')}\nMain TTS: {config.get('tts_engine')}\nFallback TTS: {config.get('fallback_tts')}", language="yaml")
    
elif page == "Ingestion Engine":
    st.header("Ingestion Engine")
    st.markdown("Paste new chapter text or fetch from a Royal Road URL to parse Dialogue and Events into the Knowledge Graph.")
    
    st.subheader("Fetch from URL (Optional)")
    with st.form("fetch_url_form"):
        url_input = st.text_input("Royal Road Chapter URL", placeholder="https://www.royalroad.com/fiction/.../chapter/...")
        fetch_submit = st.form_submit_button("Fetch Content")
        
        if fetch_submit and url_input:
            with st.spinner("Fetching chapter from Royal Road..."):
                try:
                    from app.services.royal_road_scraper import scrape_royal_road
                    scraped_data = scrape_royal_road(url_input)
                    st.session_state['fetched_title'] = scraped_data['title']
                    st.session_state['fetched_text'] = scraped_data['text']
                    st.success(f"Successfully fetched: {scraped_data['title']}")
                except Exception as e:
                    st.error(f"Failed to fetch from URL: {str(e)}")
                    
    st.divider()
    
    # Pre-fill with fetched data if available
    default_title = st.session_state.get('fetched_title', "")
    default_text = st.session_state.get('fetched_text', "")
    
    chapter_title = st.text_input("Chapter Title", value=default_title, placeholder="e.g., Chapter 1: The Beginning")
    chapter_text = st.text_area("Chapter Text", value=default_text, height=300)
    
    # Extractor Toggle
    extractor_choice = st.radio(
        "Character Extraction Method",
        ["spaCy (Fast, Rule-based)", "LLM (Smart, Context-aware)"],
        index=0,
        horizontal=True
    )
    extractor_method = "llm" if "LLM" in extractor_choice else "spacy"
    
    decay_rate = st.slider(
        "Temporal Decay Rate (Recency Weight)",
        min_value=0.0,
        max_value=1.0,
        value=0.05,
        help="Higher values make recent chapter appearances count much more than older ones for character importance.",
        step=0.01
    )
    
    if st.button("Process Chapter", type="primary"):
        if not chapter_title or not chapter_text:
            st.error("Please provide both a title and chapter text.")
        else:
            with st.spinner(f"Processing semantics and extracting events using {extractor_choice}..."):
                from app.services.ingest import ingest_chapter
                try:
                    chapter = ingest_chapter(active_story_uuid, chapter_title, chapter_text, extractor=extractor_method, decay_rate=decay_rate)
                    st.success(f"Successfully processed {chapter_title}!")
                    
                    # Display Extracted Events
                    st.subheader("Extracted Data")
                    st.json({
                        "id": chapter.id,
                        "title": chapter.title,
                        "status": "Graph Updated",
                        "extractor_used": extractor_method
                    })
                except Exception as e:
                    st.error(f"Error processing chapter: {str(e)}")

elif page == "Wiki Memory":
    st.header("Character Wiki (Memory)")
    st.markdown("Browse the generated characters and their canonical status.")
    
    from app.services.wiki import get_wiki_dir
    import os
    wiki_dir = get_wiki_dir(active_story_uuid)
    
    if os.path.exists(wiki_dir):
        files = [f for f in os.listdir(wiki_dir) if f.endswith('.md')]
        if not files:
            st.info("No characters in Wiki yet. Process some chapters first!")
        else:
            selected_file = st.selectbox("Select Character", files)
            with open(os.path.join(wiki_dir, selected_file), "r", encoding="utf-8") as f:
                content = f.read()
                
            col1, col2 = st.columns([8, 2])
            with col2:
                st.download_button(
                    label="📥 Export Wiki Entry",
                    data=content,
                    file_name=selected_file,
                    mime="text/markdown",
                    use_container_width=True
                )
                
            st.markdown("---")
            st.markdown(content)
    else:
        st.warning(f"Wiki directory '{wiki_dir}' does not exist.")
    
elif page == "Audio Hub":
    st.header("Audio Hub")
    st.markdown("Generate and test audio for graduated characters.")
    
    from app.services.ingest import load_runtime
    import yaml
    import asyncio
    
    _, runtime_db = load_runtime(active_story_uuid)
    
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    graduated_chars = [c for c in runtime_db.values() if c.voice_id is not None]
    
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
                from app.core.story_manager import StoryManager
                output_dir = os.path.join(StoryManager.DATA_DIR, active_story_uuid, "generated_audio")
                if not os.path.exists(output_dir): os.makedirs(output_dir)
                filename = os.path.join(output_dir, f"ui_test_{char.character_id}.wav")
                
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
    
    graph_engine = get_graph_engine(active_story_uuid)
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

