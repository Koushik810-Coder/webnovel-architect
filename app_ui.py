# pyre-unsafe
import streamlit as st
import streamlit.components.v1 as components  # noqa
import os

# Load .env manually to ensure API keys are available BEFORE other imports
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip().strip('"\''))

import json
import time
import math
import tempfile
import base64
import asyncio
import inspect
import yaml  # noqa
import pandas as pd  # noqa
import networkx as nx  # noqa
from pyvis.network import Network  # noqa

from app.core.story_manager import StoryManager
import app.core.story_manager as sm_mod
from app.services.ingest import (
    load_runtime, ingest_chapter, ingest_multiple_chapters,
    save_index_state, load_index_state
)
from app.services.wiki import get_wiki_dir
from app.services.scrapers.royalroad_scraper import RoyalRoadScraper
from app.services.scrapers.epub_parser import EpubParser
from app.services.audiobook_generator import generate_chapter_audiobook
from app.services.rag import query_story
from app.services.extraction import extract_chapter_intelligence, extract_chapter_intelligence_llm
from adapters.graph_adapter import GraphProvider, _graph_instances
from adapters.tts_adapter import get_tts_engine
from app.services.voice_assignment import assign_voice
from app.core.graduation import MAIN_CAST_THRESHOLD

from app.core.logger import get_logger

logger = get_logger(__name__)
if "logger_initialized" not in st.session_state:
    logger.info("Initializing Webnovel Architect Streamlit UI")
    st.session_state["logger_initialized"] = True

# --- Page Config ---
st.set_page_config(
    page_title="Webnovel Architect",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium Custom Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Base Font & Global Smoothing */
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }
    
    /* Premium Header Gradients */
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #4a90e2, #b92b27);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    
    /* Floating Glassmorphism Metric Cards */
    div[data-testid="stMetric"] {
        background: rgba(30, 30, 46, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(74, 144, 226, 0.15);
    }
    
    /* Dynamic Hover Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #4a90e2 0%, #b92b27 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(185, 43, 39, 0.4) !important;
    }
    div.stButton > button:active {
        transform: translateY(1px) scale(0.98) !important;
    }
    
    /* Stylish Inputs & Expanders */
    div[data-testid="stExpander"] {
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        background: rgba(20, 20, 30, 0.4) !important;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #4a90e2 !important;
        box-shadow: 0 0 10px rgba(74, 144, 226, 0.3) !important;
    }
    
    /* Sidebar Polish */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111118 0%, #1a1a2e 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---

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
        # Clear stale session state when switching to a different story
        if selected_uuid != st.session_state['active_story_uuid']:
            for _key in ('parsed_index_chapters', 'parsed_epub_chapters',
                         'last_ingested_index', 'saved_index_url',
                         'fetched_title', 'fetched_text'):
                st.session_state.pop(_key, None)
        st.session_state['active_story_uuid'] = selected_uuid
    
    # Create New Story
    expander_label = "➕ New Story" + (" " if st.session_state.get('new_story_toggle') else "")
    with st.expander(expander_label):
        with st.form("new_story_form"):
            new_name = st.text_input("Story Name")
            if st.form_submit_button("Create") and new_name:
                new_uuid = StoryManager.create_story(new_name)
                st.session_state['active_story_uuid'] = new_uuid
                st.session_state['nav_radio'] = "Dashboard"
                st.session_state['new_story_toggle'] = not st.session_state.get('new_story_toggle', False)
                # Clear stale index/chapter data from the previous story
                for _key in ('parsed_index_chapters', 'parsed_epub_chapters',
                             'last_ingested_index', 'saved_index_url',
                             'fetched_title', 'fetched_text'):
                    st.session_state.pop(_key, None)
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
                
            confirm_del = st.checkbox("Confirm permanent deletion", key=f"confirm_delete_{cur_uuid}")
            if st.button("🗑️ Delete Story", type="primary", use_container_width=True, disabled=not confirm_del):
                StoryManager.soft_delete_story(cur_uuid)
                st.session_state['active_story_uuid'] = None
                for _key in ('parsed_index_chapters', 'parsed_epub_chapters',
                             'last_ingested_index', 'saved_index_url',
                             'fetched_title', 'fetched_text'):
                    st.session_state.pop(_key, None)
                st.rerun()

            st.divider()
            confirm_wipe = st.checkbox("Confirm data wipe", key=f"confirm_wipe_{cur_uuid}")
            if st.button(
                "🧹 Wipe All Data",
                use_container_width=True,
                disabled=not confirm_wipe,
                help="Deletes chapters, wiki, graph, runtime, and index. Keeps the story name.",
            ):
                StoryManager.wipe_story_data(cur_uuid)
                # Evict stale in-memory graph so next access reloads from (empty) disk
                _graph_instances.pop(cur_uuid, None)
                # Clear stale session state
                for _key in ('parsed_index_chapters', 'parsed_epub_chapters',
                             'last_ingested_index', 'saved_index_url',
                             'fetched_title', 'fetched_text'):
                    st.session_state.pop(_key, None)
                st.success("All data wiped. Story is ready for fresh ingestion.")
                time.sleep(1)
                st.rerun()

    st.divider()
    
    # Navigation Radio
    page = st.radio(
        "Navigation",
        ["Dashboard", "Ingestion Engine", "Wiki Memory", "Knowledge Graph", "Story Q&A", "Audio Hub", "Export & Package", "Evaluation"],
        key="nav_radio"
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
    
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        st.error("`config.yaml` not found. Please restore it from the repository root.")
        st.stop()
        
    chapter_counter, runtime_db = load_runtime(active_story_uuid)
        
    col1, col2, col3 = st.columns(3)
    col1.metric("Processed Chapters", chapter_counter)
    col2.metric("Discovered Characters", len(runtime_db))
    # Count graduation using the actual MAIN_CAST_THRESHOLD from graduation.py
    graduated_count = len([c for c in list(runtime_db.values()) if c.confidence_score >= MAIN_CAST_THRESHOLD or c.voice_id is not None])
    col3.metric("Graduated Characters", graduated_count)
    
    st.subheader("System Configuration")
    st.code(f"LLM Engine: {config.get('llm_model')}\nMain TTS: {config.get('tts_engine')}\nFallback TTS: {config.get('fallback_tts')}", language="yaml")
    
elif page == "Ingestion Engine":
    st.header("Ingestion Engine")
    st.markdown("Paste new chapter text or fetch from a Royal Road URL to parse Dialogue and Events into the Knowledge Graph.")
    
    st.subheader("Fetch from URL (Optional)")
    
    # Load saved URL from index state — always refresh for the current story
    from app.services.ingest import load_index_state
    saved = load_index_state(active_story_uuid)
    if saved and "source_url" in saved:
        st.session_state['saved_index_url'] = saved["source_url"]
    elif 'saved_index_url' in st.session_state:
        # No saved URL for this story — clear stale value from previous story
        del st.session_state['saved_index_url']
    
    default_url = st.session_state.get('saved_index_url', "")
    
    with st.form("fetch_url_form"):
        url_input = st.text_input("Royal Road Chapter or Fiction URL", value=default_url, placeholder="https://www.royalroad.com/fiction/...")
        fetch_submit = st.form_submit_button("Fetch Content")
        
        if fetch_submit and url_input:
            with st.spinner("Fetching from Royal Road..."):
                try:
                    from app.services.scrapers.royalroad_scraper import RoyalRoadScraper
                    from app.services.ingest import save_index_state
                    scraper = RoyalRoadScraper()
                    if scraper.can_handle_index_url(url_input):
                        chapters = scraper.scrape_index(url_input)
                        st.session_state['parsed_index_chapters'] = chapters
                        
                        # Save the new index to persistence
                        save_index_state(active_story_uuid, {
                            "source_url": url_input,
                            "chapters": chapters,
                            "last_ingested_index": -1  # Indicates none of these have been ingested yet
                        })
                        
                        # Clear any existing chapter so it defaults to the new index
                        st.session_state.pop('fetched_title', None)
                        st.session_state.pop('fetched_text', None)
                        st.success(f"Successfully scraped index: {len(chapters)} chapters found!")
                    elif scraper.can_handle_url(url_input):
                        scraped_data = scraper.scrape_chapter(url_input)
                        st.session_state['fetched_title'] = scraped_data['title']
                        st.session_state['fetched_text'] = scraped_data['text']
                        # Clear parsed index if they fetched a raw chapter
                        st.session_state.pop('parsed_index_chapters', None)
                        st.success(f"Successfully fetched: {scraped_data['title']}")
                    else:
                        st.error("Currently, only Royal Road Chapter and Fiction URLs are supported.")
                except Exception as e:
                    st.error(f"Failed to fetch from URL: {str(e)}")
                    
    st.subheader("Or Upload EPUB File")
    epub_file = st.file_uploader("Upload an .epub file", type=["epub"])
    
    if epub_file is not None:
        if st.button("Parse EPUB Chapters"):
            with st.spinner("Extracting chapters from EPUB..."):
                from app.services.scrapers.epub_parser import EpubParser
                try:
                    parser = EpubParser()
                    chapters = parser.parse_epub(epub_file.read())
                    st.session_state['parsed_epub_chapters'] = chapters
                    st.success(f"Successfully extracted {len(chapters)} chapters!")
                except Exception as e:
                    st.error(f"Failed to parse EPUB: {str(e)}")
                    
    st.divider()
    
    # Pre-fill with fetched data if available
    default_title = st.session_state.get('fetched_title', "")
    default_text = st.session_state.get('fetched_text', "")
    
    # Global Ingestion Settings
    # Extractor Toggle
    extractor_choice = st.radio(
        "Character Extraction Method",
        ["spaCy (Fast, Rule-based)", "LLM (Smart, Context-aware)"],
        index=1,
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
    
    st.divider()
    
    # Attempt to load persistent index state if not in session
    if 'parsed_index_chapters' not in st.session_state:
        from app.services.ingest import load_index_state
        saved_index = load_index_state(active_story_uuid)
        if saved_index and "chapters" in saved_index:
            st.session_state['parsed_index_chapters'] = saved_index["chapters"]
            st.session_state['last_ingested_index'] = saved_index.get("last_ingested_index", -1)
            if "source_url" in saved_index:
                st.session_state['saved_index_url'] = saved_index["source_url"]
    
    # URL Index Chapter Selection
    if 'parsed_index_chapters' in st.session_state and st.session_state['parsed_index_chapters']:
        index_chapters = st.session_state['parsed_index_chapters']
        last_ingested = st.session_state.get('last_ingested_index', -1)
        next_to_ingest = last_ingested + 1
        
        st.write("### Active Index")
        st.caption(f"Scraped fiction index: {len(index_chapters)} chapters found. Last ingested index: {last_ingested} ({last_ingested + 1}/{len(index_chapters)} completed).")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            chapter_opts = {i: c['title'] for i, c in enumerate(index_chapters)}
            
            # Default to the next un-ingested chapter if available
            default_preview_idx = next_to_ingest if next_to_ingest < len(index_chapters) else max(0, len(index_chapters) - 1)
            
            selected_idx_url = st.selectbox(
                "Select Chapter to Preview", 
                options=list(chapter_opts.keys()), 
                format_func=lambda x: chapter_opts[x],
                index=default_preview_idx
            )
            
            if st.button("Load Preview"):
                with st.spinner("Fetching chapter text..."):
                    from app.services.scrapers.royalroad_scraper import RoyalRoadScraper
                    try:
                        scraper = RoyalRoadScraper()
                        scraped_data = scraper.scrape_chapter(index_chapters[selected_idx_url]['url'])
                        st.session_state['fetched_title'] = scraped_data['title']
                        st.session_state['fetched_text'] = scraped_data['text']
                        # Use rerun to immediately show the text in the text_area below
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to load chapter text: {e}")
        
        with col2:
            st.write("### Batch Ingestion")
            
            if next_to_ingest >= len(index_chapters):
                st.success("All chapters in the current index have been ingested!")
            else:
                chapters_remaining = len(index_chapters) - next_to_ingest
                batch_size = st.number_input("Number of chapters to ingest", min_value=1, max_value=chapters_remaining, value=min(5, chapters_remaining))
                
                # Setup Cancel Button above the process button
                if st.session_state.get("generating_batch", False):
                    if st.button("🚫 Stop Ingestion", type="secondary"):
                        with open("cancel_ingestion.flag", "w") as f:
                            f.write("cancel")
                        st.session_state["generating_batch"] = False
                        st.rerun()

                start_batch = st.empty()
                if not st.session_state.get("generating_batch", False):
                    if start_batch.button(f"🚀 Process Next {batch_size} Chapters", type="primary", use_container_width=True):
                        if os.path.exists("cancel_ingestion.flag"):
                            os.remove("cancel_ingestion.flag")
                        st.session_state["generating_batch"] = True
                        st.rerun()
                
                if st.session_state.get("generating_batch", False):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    from app.services.ingest import ingest_multiple_chapters, save_index_state, load_index_state

                    def update_progress(current, total):
                        progress_bar.progress(current / total)
                        status_text.text(f"Processing chapter {current} of {total}...")
                        
                        # Save state incrementally
                        new_last_index = next_to_ingest + current - 1
                        st.session_state['last_ingested_index'] = new_last_index
                        saved_state = load_index_state(active_story_uuid)
                        if saved_state is None:
                            saved_state = {}
                        saved_state["last_ingested_index"] = new_last_index
                        save_index_state(active_story_uuid, saved_state)
    
                    try:
                        chapters_to_process = index_chapters[next_to_ingest : next_to_ingest + batch_size]
                        
                        # Note: These are URLs, ingest_multiple_chapters will need to scrape them
                        ingested = ingest_multiple_chapters(
                            active_story_uuid, 
                            chapters_to_process, 
                            extractor=extractor_method, 
                            decay_rate=decay_rate,
                            progress_callback=update_progress
                        )
                        
                        if os.path.exists("cancel_ingestion.flag"):
                            with open("cancel_ingestion.flag", "r") as f:
                                stop_reason = f.read().strip()
                            if stop_reason.startswith("error:"):
                                st.error(f"Batch ingestion stopped due to an error: {stop_reason[6:].strip()}.\nSuccessfully processed {len(ingested)} chapters before stopping.")
                            else:
                                st.warning(f"Batch ingestion was stopped. Successfully processed {len(ingested)} chapters before stopping.")
                        else:
                            st.success(f"Successfully processed {len(ingested)} chapters!")
                            st.balloons()
                    except Exception as e:
                        st.error(f"Batch ingestion failed: {e}")
                    finally:
                        st.session_state["generating_batch"] = False
                        if os.path.exists("cancel_ingestion.flag"):
                            os.remove("cancel_ingestion.flag")
                        # Do not rerun automatically to prevent clearing errors/success messages immediately
                        # Let the user click 'Process Next' again.
                    
    # EPUB Chapter Selection
    elif 'parsed_epub_chapters' in st.session_state and st.session_state['parsed_epub_chapters']:
        chapters = st.session_state['parsed_epub_chapters']
        chapter_opts = {i: c['title'] for i, c in enumerate(chapters)}
        selected_idx = st.selectbox(
            "Select Chapter from EPUB", 
            options=list(chapter_opts.keys()), 
            format_func=lambda x: chapter_opts[x]
        )
        if selected_idx is not None:
            default_title = chapters[selected_idx]['title']
            default_text = chapters[selected_idx]['text']
    
    chapter_title = st.text_input("Chapter Title", value=default_title, placeholder="e.g., Chapter 1: The Beginning")
    chapter_text = st.text_area("Chapter Text", value=default_text, height=300, placeholder="Paste your chapter content here...")
    
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
    st.header("Story Wiki (Memory)")
    st.markdown("Browse the generated characters, locations, events, and narrative arcs.")
    
    from app.services.wiki import get_wiki_dir
    import os
    wiki_dir = get_wiki_dir(active_story_uuid)
    
    # Mode Selector (Applies globally to Wiki)
    col_mode, col_chap, col_pov = st.columns([2, 2, 2])
    with col_mode:
        wiki_mode = st.selectbox("Wiki View Mode", ["God Mode", "Reader Mode", "Character POV"], index=0)
        mode_map = {"God Mode": "god", "Reader Mode": "reader", "Character POV": "pov"}
        mode = mode_map[wiki_mode]
    
    with col_chap:
        from app.services.ingest import load_runtime
        chapter_counter, _ = load_runtime(active_story_uuid)
        reader_chapter = st.number_input("Reader's Current Chapter", min_value=0, max_value=chapter_counter if chapter_counter > 0 else 999, value=chapter_counter if chapter_counter > 0 else 0)
    
    with col_pov:
        if mode == "pov":
            files = []
            if os.path.exists(wiki_dir):
                files = [f for f in os.listdir(wiki_dir) if f.endswith('.md')]
            pov_options = [f.replace('.md', '') for f in files]
            pov_character_id = st.selectbox("POV Character", pov_options) if pov_options else None
        else:
            pov_character_id = None

    wiki_tab1, wiki_tab2, wiki_tab3, wiki_tab4, wiki_tab5 = st.tabs(["Characters", "Locations", "Events", "Arcs", "Dynamic Query"])

    with wiki_tab1:
        files = []
        if os.path.exists(wiki_dir):
            files = [f for f in os.listdir(wiki_dir) if f.endswith('.md')]
            
        if files:
            selected_file = st.selectbox(
                "Select Character",
                files,
                format_func=lambda f: f.replace('.md', '').replace('_', ' ').title()
            )
            if not selected_file:
                st.warning("No character selected.")
            else:
                with open(os.path.join(wiki_dir, selected_file), "r", encoding="utf-8") as f:
                    content = f.read()

                # Buttons row: spacer + two action buttons right-aligned
                _, col_rag, col_export = st.columns([5, 2, 2])

                with col_rag:
                    from app.services.wiki import enrich_wiki_from_rag
                    if st.button("✨ Improve with RAG", use_container_width=True):
                        with st.spinner("Enriching wiki using Graph RAG (respecting filters)..."):
                            char_id = selected_file.replace('.md', '')
                            try:
                                enrich_wiki_from_rag(
                                    active_story_uuid,
                                    char_id,
                                    mode=mode,
                                    reader_chapter=reader_chapter,
                                    pov_character_id=pov_character_id
                                )
                                st.success("Wiki enriched successfully!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to enrich wiki: {e}")

                with col_export:
                    st.download_button(
                        label="📥 Export Wiki Entry",
                        data=content,
                        file_name=selected_file,
                        mime="text/markdown",
                        use_container_width=True
                    )

                st.markdown("---")
                # Full-width wiki content — no column wrapper
                st.markdown(content, unsafe_allow_html=True)
        elif not os.path.exists(wiki_dir):
            st.warning(f"Wiki directory not found. Process some chapters first to generate character wikis.")
        else:
            st.info("No wiki entries found yet. Ingest some chapters to populate the wiki.")

    with wiki_tab2:
        from app.services.location_wiki import get_location_wiki_dir
        loc_dir = get_location_wiki_dir(active_story_uuid)
        loc_files = [f for f in os.listdir(loc_dir) if f.endswith('.md')] if os.path.exists(loc_dir) else []
        if loc_files:
            selected_loc = st.selectbox("Select Location", loc_files, format_func=lambda f: f.replace('.md', '').replace('_', ' ').title())
            with open(os.path.join(loc_dir, selected_loc), "r", encoding="utf-8") as f:
                st.markdown(f.read(), unsafe_allow_html=True)
        else:
            st.info("No location entries found. Locations will be extracted as you ingest chapters.")

    with wiki_tab3:
        from app.services.event_wiki import get_event_wiki_dir
        ev_dir = get_event_wiki_dir(active_story_uuid)
        ev_files = [f for f in os.listdir(ev_dir) if f.endswith('.md')] if os.path.exists(ev_dir) else []
        if ev_files:
            selected_ev = st.selectbox("Select Event", ev_files, format_func=lambda f: f.replace('.md', '').replace('_', ' ').title())
            with open(os.path.join(ev_dir, selected_ev), "r", encoding="utf-8") as f:
                st.markdown(f.read(), unsafe_allow_html=True)
        else:
            st.info("No event entries found. Events will be extracted as you ingest chapters.")

    with wiki_tab4:
        from app.services.arc_wiki import get_arc_wiki_dir
        arc_dir = get_arc_wiki_dir(active_story_uuid)
        arc_files = [f for f in os.listdir(arc_dir) if f.endswith('.md')] if os.path.exists(arc_dir) else []
        if arc_files:
            selected_arc = st.selectbox("Select Arc", arc_files, format_func=lambda f: f.replace('.md', '').replace('_', ' ').title())
            with open(os.path.join(arc_dir, selected_arc), "r", encoding="utf-8") as f:
                st.markdown(f.read(), unsafe_allow_html=True)
        else:
            st.info("No narrative arc entries found. Arcs are detected in batches every 5 chapters.")

    with wiki_tab5:
        st.subheader("Graph Query Language")
        st.markdown("Use natural language to project dynamic, filtered wiki pages based on complex graph queries.")
        
        query_examples = [
            "Show me Alice before the betrayal",
            "Show Ravi from Alice's perspective",
            "Show all hidden knowledge events",
            "What is the full truth of this arc?"
        ]
        
        with st.form("dynamic_query_form"):
            user_query = st.text_input("Enter your graph query:", placeholder="e.g. Show me the events at the academy before the invasion.")
            st.caption("Examples: " + ", ".join([f"*{ex}*" for ex in query_examples]))
            
            submit_query = st.form_submit_button("Generate Projection", type="primary")
            
            if submit_query and user_query:
                with st.spinner("Parsing intent, filtering graph nodes, and generating projection..."):
                    from app.services.rag import query_story_with_filter
                    try:
                        projection = query_story_with_filter(
                            active_story_uuid, 
                            user_query, 
                            mode=mode, 
                            reader_chapter=reader_chapter,
                            pov_character_id=pov_character_id
                        )
                        st.success("Projection generated!")
                        st.markdown("---")
                        st.markdown(projection)
                    except Exception as e:
                        st.error(f"Failed to process query: {e}")
    
elif page == "Audio Hub":
    st.header("Audio Hub")
    st.markdown("Generate and test audio for graduated characters.")
    
    from app.services.ingest import load_runtime
    import yaml
    import asyncio
    
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        st.error("`config.yaml` not found. Please restore it from the repository root.")
        st.stop()
        
    chapter_counter, runtime_db = load_runtime(active_story_uuid)
    
    st.subheader("📚 Full Chapter Audiobook")
    st.markdown("Synthesize a dynamic, multi-voice audiobook for a complete chapter. (Bypasses graduation threshold)")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        chapter_to_sync = st.number_input("Chapter Number", min_value=1, max_value=chapter_counter if chapter_counter > 0 else 1, value=1)
    with col2:
        engine_type_ab = st.radio("Audiobook Engine", [config.get('tts_engine', 'kokoro'), config.get('fallback_tts', 'edge_tts')], horizontal=True)
    with col3:
        # Define cancel flag button logic
        if st.session_state.get("generating_audiobook", False):
            if st.button("🚫 Cancel Generation", type="secondary"):
                with open("cancel_audio.flag", "w") as f:
                    f.write("cancel")
                st.session_state["generating_audiobook"] = False
                st.rerun()
        else:
            # Add a button to wipe cached_script.json and force re-extraction
            from app.core.story_manager import StoryManager
            import os
            script_cache_path = os.path.join(StoryManager.DATA_DIR, active_story_uuid, "chapters", str(chapter_to_sync), "cached_script.json")
            if os.path.exists(script_cache_path):
                st.caption("✅ Script is currently cached (fast render).")
                if st.button("🔄 Regenerate Script", help="Deletes the cached LLM dialogue script so it correctly re-parses with the new rules."):
                    os.remove(script_cache_path)
                    st.success("Script cache cleared! The LLM will re-extract during the next generation.")
                    st.rerun()
            else:
                st.caption("⚠️ No script cached yet — will generate fresh.")

    # Generation Button
    start_placeholder = st.empty()
    if not st.session_state.get("generating_audiobook", False):
        if start_placeholder.button("Synthesize Entire Chapter", type="primary", disabled=chapter_counter == 0):
            if chapter_counter == 0:
                st.warning("No chapters processed yet.")
            else:
                if os.path.exists("cancel_audio.flag"):
                    os.remove("cancel_audio.flag")
                st.session_state["generating_audiobook"] = True
                st.rerun()

    if st.session_state.get("generating_audiobook", False):
        with st.spinner(f"Extracting LLM script and rendering audio for Chapter {chapter_to_sync}..."):
            from app.services.audiobook_generator import generate_chapter_audiobook
            try:
                result = generate_chapter_audiobook(active_story_uuid, chapter_to_sync, engine=engine_type_ab)
                if result:
                    st.session_state["ab_success_msg"] = f"Audiobook for Chapter {chapter_to_sync} complete!"
                else:
                    if os.path.exists("cancel_audio.flag"):
                        st.info("Generation cancelled by user.")
                    else:
                        logger.error(f"Audiobook generation returned None for chapter {chapter_to_sync} (engine: {engine_type_ab}). Check log above for details.")
                        st.error("Audiobook generation failed. Check the log file for details.")
            except Exception as e:
                logger.error(f"Audiobook generation exception for chapter {chapter_to_sync}: {type(e).__name__}: {e}")
                st.error(f"Error generating audiobook: {e}")
            finally:
                st.session_state["generating_audiobook"] = False
                if os.path.exists("cancel_audio.flag"):
                    os.remove("cancel_audio.flag")
                st.rerun()

    # Serve Audio Player Statically from Disk
    final_audio_path = os.path.join(StoryManager.DATA_DIR, active_story_uuid, "generated_audio", f"chapter_{chapter_to_sync}_full.mp3")
    final_vtt_path = os.path.join(StoryManager.DATA_DIR, active_story_uuid, "generated_audio", f"chapter_{chapter_to_sync}_full.vtt")

    if st.session_state.get("ab_success_msg"):
        st.success(st.session_state["ab_success_msg"])
        st.session_state.pop("ab_success_msg", None)  # consume once

    if os.path.exists(final_audio_path) and os.path.exists(final_vtt_path):
        import base64
        with open(final_audio_path, "rb") as f:
            audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        with open(final_vtt_path, "r", encoding="utf-8") as f:
            vtt_text = f.read()
        vtt_b64 = base64.b64encode(vtt_text.encode('utf-8')).decode('utf-8')
        
        html_player = f"""
        <div style="background-color: #1e1e2e; padding: 20px; border-radius: 10px; margin-top: 10px;">
            <h4 style="color: white; margin-bottom: 15px;">Chapter {chapter_to_sync} Playback</h4>
            <video controls style="width: 100%; height: 60px; background-color: #000; border-radius: 5px;" name="media">
                <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mpeg">
                <track label="English" kind="subtitles" srclang="en" src="data:text/vtt;base64,{vtt_b64}" default>
                Your browser does not support the audio element or WebVTT.
            </video>
            <p style="color: #aaa; font-size: 12px; margin-top: 10px;">Turn on CC in the player to see the synchronized text.</p>
        </div>
        """
        st.components.v1.html(html_player, height=150)
                    
    st.divider()
    st.subheader("🎙️ Character Voice Testing")
    
    graduated_chars = [c for c in runtime_db.values() if c.confidence_score >= MAIN_CAST_THRESHOLD or c.voice_id is not None]
    
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
                os.makedirs(output_dir, exist_ok=True)
                filename = os.path.join(output_dir, f"ui_test_{char.character_id}.wav")
                
                try:
                    # Provide voice_id if None
                    if not voice:
                        from app.services.voice_assignment import assign_voice
                        voice = assign_voice(char)
                        
                    if asyncio.iscoroutinefunction(tts.generate_audio):
                        from app.services.audiobook_generator import _run_async
                        _run_async(tts.generate_audio(test_text, voice, filename))
                    else:
                        tts.generate_audio(test_text, voice, filename)
                        
                    st.success("Audio generated!")
                    with open(filename, "rb") as _af:
                        st.audio(_af.read(), format="audio/wav")
                except Exception as e:
                    st.error(f"Failed to generate audio: {str(e)}")
elif page == "Knowledge Graph":
    st.header("Knowledge Graph")
    st.markdown("Interactive visualization of the character relationship graph built from ingested chapters.")
    
    from adapters.graph_adapter import GraphProvider
    from pyvis.network import Network
    import streamlit.components.v1 as components
    import tempfile
    
    # Force load latest graph from disk
    from adapters.graph_adapter import get_graph_engine
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
            if relation == "causes":
                net.add_edge(str(src), str(dst), title=relation, color="#ffaa00", dashes=True) # Orange dashed line for causality
            else:
                net.add_edge(str(src), str(dst), title=relation, color="#888")
        
        # Save to temp HTML, embed, then clean up
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as _tf:
            html_path = _tf.name
        try:
            net.save_graph(html_path)
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
        finally:
            try:
                os.unlink(html_path)
            except OSError:
                pass

        st.caption("🔴 Character Nodes   🔵 Event Nodes   🟠 Causal Links (dashed)")
        components.html(html_content, height=700, scrolling=False)
        
        # Stats below
        col1, col2 = st.columns(2)
        char_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "character"]
        event_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "event"]
        col1.metric("Character Nodes", len(char_nodes))
        col2.metric("Event Nodes", len(event_nodes))

elif page == "Story Q&A":
    st.header("Story Q&A (Time-CoT RAG)")
    st.markdown("Ask temporal and contextual questions about the story. The engine uses DyG-RAG principles (Chronological Dynamic Event Units) to reason through the character timelines.")
    
    # Initialize chat history
    chat_key = f"chat_history_{active_story_uuid}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
        
    # Add a clear button to the expander
    with st.expander("🔍 Filtering & Spoiler Controls"):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            qa_mode_sel = st.selectbox("Answer Perspective", ["Full Knowledge (Spoilers)", "Reader Safe (No Spoilers)"], index=0)
            qa_mode = "god" if "Full" in qa_mode_sel else "reader"
        with col2:
            from app.services.ingest import load_runtime
            chapter_counter, _ = load_runtime(active_story_uuid)
            qa_reader_chapter = st.number_input("Assume Reader at Chapter", min_value=0, max_value=chapter_counter if chapter_counter > 0 else 999, value=chapter_counter if chapter_counter > 0 else 0, key="qa_chapter")
        with col3:
            st.write("") # spacing
            st.write("")
            if st.button("🗑️ Clear Chat"):
                st.session_state[chat_key] = []
                st.rerun()

    # Display chat messages from history
    for message in st.session_state[chat_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask a question about the story..."):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Add user message to chat history
        st.session_state[chat_key].append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Traversing the event graph and reasoning through the timeline..."):
                from app.services.rag import query_story
                try:
                    # Pass history EXCEPT the very last message (which is the current query)
                    history_for_rag = st.session_state[chat_key][:-1]
                    
                    answer = query_story(
                        active_story_uuid, 
                        prompt, 
                        mode=qa_mode, 
                        reader_chapter=qa_reader_chapter,
                        chat_history=history_for_rag
                    )
                    message_placeholder.markdown(answer)
                    st.session_state[chat_key].append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Failed to generate answer: {e}")
                    # Remove the failed user prompt so it doesn't get stuck
                    st.session_state[chat_key].pop()

elif page == "Export & Package":
    st.header("Export & Package Audiobook")
    st.markdown("Compile your generated chapter audio into downloadable formats.")
    
    from app.services.export import export_audiobook_zip, export_audiobook_html, export_single_audiobook
    import os
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Raw ZIP")
        st.caption("A simple ZIP containing all chapter MP3s and VTTs.")
        if st.button("Package ZIP"):
            with st.spinner("Packaging..."):
                try:
                    zip_path = export_audiobook_zip(active_story_uuid)
                    with open(zip_path, "rb") as f:
                        st.download_button("Download ZIP", f.read(), file_name=os.path.basename(zip_path), mime="application/zip", key="dl_zip")
                    st.success("Successfully packaged raw ZIP!")
                except Exception as e:
                    st.error(f"Error: {e}")
                    
    with col2:
        st.subheader("Web Player ZIP")
        st.caption("A ZIP containing a stylish HTML web player pre-loaded with all chapters.")
        if st.button("Package Web Player"):
            with st.spinner("Packaging..."):
                try:
                    zip_path = export_audiobook_html(active_story_uuid)
                    with open(zip_path, "rb") as f:
                        st.download_button("Download Web Player", f.read(), file_name=os.path.basename(zip_path), mime="application/zip", key="dl_web")
                    st.success("Successfully packaged web player!")
                except Exception as e:
                    st.error(f"Error: {e}")
                    
    with col3:
        st.subheader("Single MP3 Audiobook")
        st.caption("Stitch all chapters into one massive MP3 file using FFmpeg.")
        if st.button("Stitch Audiobook"):
            with st.spinner("Stitching via FFmpeg... This may take a while."):
                try:
                    mp3_path, vtt_path = export_single_audiobook(active_story_uuid)
                    with open(mp3_path, "rb") as f:
                        st.download_button("Download Full MP3", f.read(), file_name=os.path.basename(mp3_path), mime="audio/mpeg", key="dl_full_mp3")
                    st.success("Successfully stitched single audiobook!")
                except Exception as e:
                    st.error(f"Error: {e}")



elif page == "Evaluation":
    import json
    import time
    import math
    import os
    import tempfile
    import streamlit as st

    st.header("Phase 6 — Evaluation Harness")
    st.markdown(
        "Runs the four quantitative metrics from the Review 1 deck against the gold-standard "
        "annotation in `dataset/gold_standard.json`."
    )

    GOLD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset", "gold_standard.json")

    if not os.path.exists(GOLD_PATH):
        st.error(f"Gold-standard file not found: `{GOLD_PATH}`")
        st.stop()

    with open(GOLD_PATH, "r", encoding="utf-8") as _f:
        gold_data = json.load(_f)

    run_llm = st.checkbox("Include LLM extraction metric (makes API call)", value=False)
    run_tts = st.checkbox("Include TTS Real-Time Factor metric", value=True)

    if st.button("▶ Run Evaluation", type="primary"):

        # ── helpers ──────────────────────────────────────────────────────────
        def prf(predicted, gold):
            ps = {x.lower() for x in predicted}
            gs = {x.lower() for x in gold}
            if not ps:
                return 0.0, 0.0, 0.0
            p = len(ps & gs) / len(ps)
            r = len(ps & gs) / len(gs) if gs else 0.0
            f = (2*p*r/(p+r)) if (p+r) else 0.0
            return p, r, f

        text       = gold_data["text"]
        gold_chars = gold_data["gold_characters"]
        gold_world = gold_data["gold_world_terms"]
        gold_all   = gold_chars + gold_world

        # ── Metric 1 — Entity P/R/F1 ─────────────────────────────────────────
        with st.expander("📐 Metric 1 — Entity Precision / Recall / F1", expanded=True):
            from app.services.extraction import extract_chapter_intelligence

            t0 = time.perf_counter()
            res_spacy  = extract_chapter_intelligence(text)
            spacy_ms   = (time.perf_counter() - t0) * 1000
            sc = res_spacy.get("active_character_names", [])
            sw = res_spacy.get("active_world_terms", [])

            rows = []
            for label, pred, gold in [
                ("Characters (spaCy)",  sc, gold_chars),
                ("World Terms (spaCy)", sw, gold_world),
                ("Combined (spaCy)",    sc+sw, gold_all),
            ]:
                p, r, f = prf(pred, gold)
                rows.append({"Label": label, "Precision": f"{p:.0%}", "Recall": f"{r:.0%}", "F1": f"{f:.0%}"})

            if run_llm:
                from app.services.extraction import extract_chapter_intelligence_llm
                with st.spinner("Calling LLM…"):
                    try:
                        t0 = time.perf_counter()
                        res_llm  = extract_chapter_intelligence_llm(text)
                        llm_ms   = (time.perf_counter() - t0) * 1000
                        lc = res_llm.get("active_character_names", [])
                        lw = res_llm.get("active_world_terms", [])
                        for label, pred, gold in [
                            ("Characters (LLM)",  lc, gold_chars),
                            ("World Terms (LLM)", lw, gold_world),
                            ("Combined (LLM)",    lc+lw, gold_all),
                        ]:
                            p, r, f = prf(pred, gold)
                            rows.append({"Label": label, "Precision": f"{p:.0%}", "Recall": f"{r:.0%}", "F1": f"{f:.0%}"})
                    except Exception as e:
                        st.warning(f"LLM extraction failed: {e}")

            import pandas as pd
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.caption(f"spaCy extraction took {spacy_ms:.0f} ms")

        # ── Metric 2 — Graph Latency ──────────────────────────────────────────
        with st.expander("⚡ Metric 2 — Graph Traversal Latency", expanded=True):
            import networkx as nx
            import app.core.story_manager as sm_mod
            from adapters.graph_adapter import GraphProvider

            lat_rows = []
            with tempfile.TemporaryDirectory() as tmpd:
                orig = sm_mod.StoryManager.DATA_DIR
                sm_mod.StoryManager.DATA_DIR = tmpd
                try:
                    for n in [10, 50, 100, 500, 1000]:
                        gp = GraphProvider("bench")
                        for i in range(n):
                            gp.graph.add_node(f"c{i}", type="character", last_seen_chapter=i)
                            ev = f"e{i}"
                            gp.graph.add_node(ev, type="event", chapter_id=i)
                            gp.graph.add_edge(f"c{i}", ev, relation="participant", chapter_id=i)
                            gp.graph.add_edge(ev, f"c{i}", relation="featured",    chapter_id=i)
                        t0 = time.perf_counter()
                        gp.get_character_importance("c0", current_chapter=n, decay_rate=0.05)
                        ms = (time.perf_counter() - t0) * 1000
                        lat_rows.append({"Graph Size (nodes)": n*2, "Lookup Latency (ms)": f"{ms:.1f}", "Target": "< 500 ms", "Pass": "✓" if ms < 500 else "✗"})
                        gp.graph = nx.DiGraph()
                finally:
                    sm_mod.StoryManager.DATA_DIR = orig

            st.dataframe(pd.DataFrame(lat_rows), use_container_width=True, hide_index=True)

        # ── Metric 3 — TTS RTF ───────────────────────────────────────────────
        if run_tts:
            with st.expander("🔊 Metric 3 — TTS Real-Time Factor (RTF)", expanded=True):
                BENCH_TEXT = (
                    "The warrior stood at the edge of the realm, his voice echoing across the valley. "
                    "He had journeyed for seven years to reach this moment."
                )
                approx_dur = len(BENCH_TEXT.split()) / 150.0

                tried = False
                for eng in ["kokoro", "edge"]:
                    try:
                        from adapters.tts_adapter import get_tts_engine
                        tts = get_tts_engine(eng)
                        # Determine safe mock voice IDs for the test
                        mock_voice = "af_heart" if eng == "kokoro" else "en-US-AriaNeural"
                        
                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                            out_p = tf.name
                        import asyncio
                        import inspect
                        with st.spinner(f"Synthesizing with {eng}…"):
                            t0 = time.perf_counter()
                            if inspect.iscoroutinefunction(tts.generate_audio):
                                asyncio.run(tts.generate_audio(BENCH_TEXT, mock_voice, out_p))
                            else:
                                tts.generate_audio(BENCH_TEXT, mock_voice, out_p)
                            wall = time.perf_counter() - t0
                        rtf = wall / approx_dur
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Engine", eng)
                        c2.metric("RTF", f"{rtf:.3f}", delta="< 1.0 target", delta_color="normal" if rtf < 1.0 else "inverse")
                        c3.metric("Gen Time", f"{wall:.2f}s")
                        try: os.remove(out_p)
                        except OSError: pass
                        tried = True
                        break
                    except Exception as e:
                        st.caption(f"{eng} unavailable: {e}")
                if not tried:
                    st.warning("No TTS engine available. Install kokoro or edge-tts.")

        # ── Metric 4 — Spearman ρ ────────────────────────────────────────────
        with st.expander("📊 Metric 4 — Spearman ρ Rank Correlation", expanded=True):
            import app.core.story_manager as sm_mod
            from adapters.graph_adapter import _graph_instances

            expected_rank = gold_data.get("expected_rank_order", [])

            def to_id(n):
                return n.lower().replace(" ", "_").replace("'", "")

            expected_ids = [to_id(n) for n in expected_rank]

            with tempfile.TemporaryDirectory() as tmpd:
                orig = sm_mod.StoryManager.DATA_DIR
                sm_mod.StoryManager.DATA_DIR = tmpd
                _graph_instances.pop("bench", None)  # Only clear our benchmark key
                try:
                    from app.services.ingest import ingest_chapter, load_runtime
                    story_id = sm_mod.StoryManager.create_story("eval_rho")
                    ingest_chapter(story_id, "Gold Chapter", text, extractor="spacy")
                    _, rdb = load_runtime(story_id)
                    computed_sorted = sorted(rdb.values(), key=lambda c: c.confidence_score, reverse=True)
                    computed_rank   = [c.character_id for c in computed_sorted]

                    common = [x for x in expected_ids if x in computed_rank]
                    n_c = len(common)

                    def spearman(a, b):
                        if len(a) < 2: return float("nan")
                        pa = {x: i for i, x in enumerate(a)}
                        pb = {x: i for i, x in enumerate(b)}
                        d2 = sum((pa[x] - pb[x])**2 for x in a if x in pb)
                        n  = len(a)
                        return 1 - (6*d2)/(n*(n**2-1))

                    rho = spearman(expected_ids, computed_rank)

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Spearman ρ", f"{rho:.3f}" if not math.isnan(rho) else "N/A")
                    c2.metric("Common Chars Compared", n_c)
                    c3.metric("Target", "ρ ≥ 0.70")

                    # Pad computed rank with blanks if it's shorter than expected, and truncate if longer
                    display_computed = computed_rank + [""] * max(0, len(expected_rank) - len(computed_rank))
                    display_computed = display_computed[:len(expected_rank)]

                    rank_df = pd.DataFrame({
                        "Human Rank":    expected_rank,
                        "Computed ID":   display_computed
                    })
                    st.dataframe(rank_df, use_container_width=True, hide_index=False)

                except Exception as e:
                    st.error(f"Spearman metric failed: {e}")
                finally:
                    _graph_instances.pop(story_id, None)  # Only clear eval key
                    sm_mod.StoryManager.DATA_DIR = orig
