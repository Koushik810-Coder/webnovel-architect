import os

file_path = "c:\\Projects\\webnovel-architect\\app_ui.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix 2: Session resets
# 1. Insert helper
helper_code = """
def clear_story_session_state():
    for _key in ('parsed_index_chapters', 'parsed_epub_chapters',
                 'last_ingested_index', 'saved_index_url',
                 'fetched_title', 'fetched_text', 'previewed_index'):
        st.session_state.pop(_key, None)
"""
if "def clear_story_session_state()" not in content:
    content = content.replace(
        '    st.session_state["logger_initialized"] = True',
        '    st.session_state["logger_initialized"] = True\n' + helper_code
    )

# Replace instances of the loop
session_loop1 = """        if selected_uuid != st.session_state['active_story_uuid']:
            for _key in ('parsed_index_chapters', 'parsed_epub_chapters',
                         'last_ingested_index', 'saved_index_url',
                         'fetched_title', 'fetched_text'):
                st.session_state.pop(_key, None)"""
session_repl1 = """        if selected_uuid != st.session_state['active_story_uuid']:
            clear_story_session_state()"""
content = content.replace(session_loop1, session_repl1)

session_loop2 = """                # Clear stale index/chapter data from the previous story
                for _key in ('parsed_index_chapters', 'parsed_epub_chapters',
                             'last_ingested_index', 'saved_index_url',
                             'fetched_title', 'fetched_text'):
                    st.session_state.pop(_key, None)"""
session_repl2 = """                # Clear stale index/chapter data from the previous story
                clear_story_session_state()"""
content = content.replace(session_loop2, session_repl2)

session_loop3 = """                for _key in ('parsed_index_chapters', 'parsed_epub_chapters',
                             'last_ingested_index', 'saved_index_url',
                             'fetched_title', 'fetched_text'):
                    st.session_state.pop(_key, None)"""
session_repl3 = """                clear_story_session_state()"""
content = content.replace(session_loop3, session_repl3)

session_loop4 = """                # Clear stale session state
                for _key in ('parsed_index_chapters', 'parsed_epub_chapters',
                             'last_ingested_index', 'saved_index_url',
                             'fetched_title', 'fetched_text'):
                    st.session_state.pop(_key, None)"""
session_repl4 = """                # Clear stale session state
                clear_story_session_state()"""
content = content.replace(session_loop4, session_repl4)


# Fix 1: Concurrent Data Corruption
eval_tmp1 = """            with tempfile.TemporaryDirectory() as tmpd:
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
                    sm_mod.StoryManager.DATA_DIR = orig"""
eval_repl1 = """            try:
                for n in [10, 50, 100, 500, 1000]:
                    gp = GraphProvider("bench_eval_temp")
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
                sm_mod.StoryManager.wipe_story_data("bench_eval_temp")
                sm_mod.StoryManager.soft_delete_story("bench_eval_temp")
                _graph_instances.pop("bench_eval_temp", None)"""
content = content.replace(eval_tmp1, eval_repl1)

eval_tmp2 = """            with tempfile.TemporaryDirectory() as tmpd:
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
                    sm_mod.StoryManager.DATA_DIR = orig"""

eval_repl2 = """            try:
                from app.services.ingest import ingest_chapter, load_runtime
                story_id = sm_mod.StoryManager.create_story("eval_rho_temp")
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
                if 'story_id' in locals():
                    sm_mod.StoryManager.wipe_story_data(story_id)
                    sm_mod.StoryManager.soft_delete_story(story_id)
                    _graph_instances.pop(story_id, None)"""
content = content.replace(eval_tmp2, eval_repl2)

# Fix 3: Remove useless re-imports
# Dashboard imports
content = content.replace("    import yaml\n    from app.services.ingest import load_runtime\n    \n    try:", "    try:")
# Audio Hub imports
content = content.replace("    from app.services.ingest import load_runtime\n    import yaml\n    import asyncio\n    \n    try:", "    try:")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Applied audit fixes")
