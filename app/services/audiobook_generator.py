# pyre-unsafe
import os
import json
import asyncio
import subprocess
from app.core.story_manager import StoryManager
from app.services.ingest import load_runtime, normalize_id
from adapters.llm_adapter import analyze_text_json
import yaml

from app.core.logger import get_logger
logger = get_logger(__name__)

def _run_async(coro):
    """
    Safely executes an asynchronous coroutine, adapting to whether an event loop is already running.
    
    This is useful for bridging async code with synchronous contexts (like Streamlit callbacks)
    that may or may not already have an active event loop.
        
    Args:
        coro: The async coroutine object to run.
        
    Returns:
        The result of the wrapped coroutine execution.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We are inside an existing event loop (e.g. Streamlit).
        # Create a brand-new loop in a background thread.
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(lambda c=coro: asyncio.run(c))
            return future.result()
    else:
        return asyncio.run(coro)


def generate_chapter_audiobook(story_uuid: str, chapter_id: int, engine: str = "edge"):
    """
    Generates a full-chapter MP3 audiobook.
    
    This pipeline extracts a script separating narrator and character dialogue using an LLM,
    assigns consistent voices to characters using the project's runtime configuration, generates
    audio chunks for each script segment via the requested TTS engine, and stitches them
    alongside VTT subtitles using FFmpeg.
    
    Args:
        story_uuid (str): The unique identifier for the story.
        chapter_id (int): The ID of the chapter to generate audio for.
        engine (str): The TTS engine to use ('edge' or 'kokoro').
        
    Returns:
        Optional[Tuple[str, str]]: Paths to the final compiled audio (MP3) and subtitle (VTT)
            files if successful, otherwise None.
    """

    # ── 1. Load Chapter Text ──────────────────────────────────────────────
    chapter_dir = os.path.join(StoryManager.DATA_DIR, story_uuid, "chapters", str(chapter_id))
    text_path = os.path.join(chapter_dir, "text.txt")
    if not os.path.exists(text_path):
        raise FileNotFoundError(f"Chapter {chapter_id} text not found at {text_path}")

    with open(text_path, "r", encoding="utf-8") as f:
        chapter_text = f.read()

    # ── 2. Extract Script via LLM ─────────────────────────────────────────
    script_path = os.path.join(chapter_dir, "cached_script.json")
    if os.path.exists(script_path):
        logger.info(f"Loading cached script from {script_path}")
        with open(script_path, "r", encoding="utf-8") as f:
            script = json.load(f)
    else:
        # Chunk the chapter to avoid LLM output token limits and ensure full coverage
        MAX_CHAR_CHUNK = 6000
        paragraphs = chapter_text.split('\n\n')
        text_chunks = []
        current_chunk = ""
        for p in paragraphs:
            if len(current_chunk) + len(p) < MAX_CHAR_CHUNK:
                current_chunk += p + "\n\n"
            else:
                if current_chunk:
                    text_chunks.append(current_chunk.strip())
                current_chunk = p + "\n\n"
        if current_chunk:
            text_chunks.append(current_chunk.strip())

        if not text_chunks:
            text_chunks = [chapter_text]

        full_script = []
        
        for idx, chunk in enumerate(text_chunks):
            logger.info(f"Extracting script from chunk {idx+1}/{len(text_chunks)} via LLM...")
            prompt = f"""
Convert this chapter text into an audiobook script. Break the text into logical segments.
For each segment, determine if it is narration (spoken by the narrator) or dialogue (spoken by a specific character).
Ensure every word from the text is included in a segment so the entire text is narrated seamlessly.

Return a JSON object with a single list 'script'.
Each item in the list should be an object: {{"speaker": "Narrator" or "Character Name", "text": "The actual text to read"}}

For dialogue, try to guess the character speaking if it is obvious from context. If it is narration, use "Narrator".

Chapter Text:
{chunk}
"""
            try:
                script_res = analyze_text_json(prompt)
                
                # Check if default LLM hit rate limits and fell back to emitting an error dict
                if "error" in script_res:
                    logger.warning(f"Primary LLM failed for chunk {idx+1}. Trying fallback to Gemini...")
                    script_res = analyze_text_json(prompt, model="gemini/gemini-2.5-flash")
                
                script_list = script_res.get("script", [])
                if not script_list:
                    raise ValueError("LLM returned empty script list")
                full_script.extend(script_list)
            except Exception as e:
                raise RuntimeError(f"LLM extraction completely failed for chunk {idx+1}. Please verify your API keys and internet connection, or try again later. Details: {e}")

        script = full_script
        logger.info(f"Script has {len(script)} segments total. Saving cache...")
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(script, f, indent=4)

    # ── 3. Load Runtime for character voices ──────────────────────────────
    _, runtime_db = load_runtime(story_uuid)

    from adapters.tts_adapter import get_tts_engine
    tts_engine_obj = get_tts_engine(engine)

    if engine == "kokoro":
        NARRATOR_VOICE = "am_adam"
        CHARACTER_VOICES = ["af_bella", "af_nicole", "af_sarah", "am_michael", "bm_george", "bf_emma"]
    else:
        NARRATOR_VOICE = "en-US-GuyNeural"
        CHARACTER_VOICES = [
            "en-US-AriaNeural",
            "en-US-JennyNeural",
            "en-US-DavisNeural",
            "en-US-TonyNeural",
            "en-GB-SoniaNeural",
            "en-GB-RyanNeural",
        ]
    _voice_assignments: dict = {}  # speaker name -> edge voice
    _voice_idx = [0]

    def _get_voice_for_speaker(speaker: str) -> str:
        if speaker == "Narrator":
            return NARRATOR_VOICE

        char_id = normalize_id(speaker)
        # Check if the runtime already has a voice compatible with current engine
        if char_id in runtime_db and runtime_db[char_id].voice_id:
            v_id = runtime_db[char_id].voice_id
            is_edge = v_id.startswith("en-")
            if (engine == "edge" and is_edge) or (engine == "kokoro" and not is_edge):
                return v_id

        # Assign a consistent voice from the pool
        if speaker not in _voice_assignments:
            _voice_assignments[speaker] = CHARACTER_VOICES[_voice_idx[0] % len(CHARACTER_VOICES)]
            _voice_idx[0] += 1
        return _voice_assignments[speaker]

    # ── 4. Synthesize Audio Chunks ────────────────────────────────────────
    output_dir = os.path.join(StoryManager.DATA_DIR, story_uuid, "generated_audio", f"chapter_{chapter_id}")
    os.makedirs(output_dir, exist_ok=True)

    chunk_files = []
    
    # We will accumulate subtitle objects here. Each chunk will have its own subtitles starting from 0,
    # so we'll need to offset them by the duration of previous chunks.
    # We'll use pydub to easily measure audio durations if available, 
    # but to keep it simple, EdgeTTS SubMaker outputs literal time strings, we can just save a separate VTT per chunk
    # and concat them mathematically, or since ffconcat supports metadata merging, we might just write a parser for the timestamps.
    # Actually, the easiest and robust way without extra deps (like pydub) is to just generate the VTT blocks, 
    # and calculate lengths via ffmpeg later, or just use the submaker directly on the final stiched text (which doesn't work well due to voice swapping).
    # Since we use `ffmpeg concat`, it's actually complicated to merge VTTs without reading the audio length.
    # Let's use a simpler heuristic: we will write individual `.vtt` files for each chunk, and use a python script to merge them by reading their lengths via ffprobe.
    
    import math

    def get_audio_duration(file_path):
        """Returns audio duration in seconds using ffprobe."""
        try:
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception as e:
            logger.warning(f"Could not get duration for {file_path}: {e}")
            return 0.0

    def offset_vtt_timestamps(vtt_text: str, offset_seconds: float) -> str:
        """Adds offset_seconds to all timestamps in a VTT block."""
        import re
        
        def add_seconds(time_str, offset):
            # Parse HH:MM:SS.mmm
            parts = time_str.split(':')
            h, m = int(parts[0]), int(parts[1])
            s, ms = [int(x) for x in parts[2].split('.')]
            
            total_seconds = (h * 3600) + (m * 60) + s + (ms / 1000.0) + offset
            
            new_h = int(total_seconds // 3600)
            total_seconds %= 3600
            new_m = int(total_seconds // 60)
            total_seconds %= 60
            new_s = int(total_seconds)
            new_ms = int(round((total_seconds - new_s) * 1000))
            
            return f"{new_h:02d}:{new_m:02d}:{new_s:02d}.{new_ms:03d}"

        def replace_match(match):
            start = add_seconds(match.group(1), offset_seconds)
            end = add_seconds(match.group(2), offset_seconds)
            return f"{start} --> {end}"
            
        return re.sub(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s-->\s(\d{2}:\d{2}:\d{2}\.\d{3})', replace_match, vtt_text)

    chunk_vtts = []

    for i, segment in enumerate(script):
        if os.path.exists("cancel_audio.flag"):
            logger.info("Cancellation requested.")
            return None
            
        speaker = segment.get("speaker", "Narrator")
        text = segment.get("text", "").strip()
        if not text:
            continue

        voice = _get_voice_for_speaker(speaker)
        chunk_path = os.path.join(output_dir, f"{i:04d}_{speaker.replace(' ', '_')}.mp3")
        vtt_chunk_path = os.path.join(output_dir, f"{i:04d}_{speaker.replace(' ', '_')}.vtt")

        logger.debug(f"[{i+1}/{len(script)}] {speaker} ({voice}): {text[:40]}...")
        
        async def _synthesize_edge_tts(t, v, p, p_vtt):
            import edge_tts
            from edge_tts.submaker import SubMaker
            comm = edge_tts.Communicate(t, v)
            submaker = SubMaker()
            with open(p, "wb") as file:
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        file.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        submaker.feed(chunk)
            with open(p_vtt, "w", encoding="utf-8") as file:
                file.write(submaker.get_srt().replace(',', '.'))

        def _synthesize_kokoro(t, v, p, p_vtt):
            tts_engine_obj.generate_audio(t, v, p)
            dur = get_audio_duration(p)
            def _fmt(s):
                h, m, sec, ms = int(s // 3600), int((s % 3600) // 60), int(s % 60), int((s - int(s)) * 1000)
                return f"{h:02d}:{m:02d}:{sec:02d}.{ms:03d}"
            with open(p_vtt, "w", encoding="utf-8") as file:
                file.write(f"1\n00:00:00.000 --> {_fmt(dur)}\n{t}\n")

        import time
        max_retries: int = 3 if engine != "kokoro" else 1
        for attempt in range(max_retries):
            try:
                if engine == "kokoro":
                    _synthesize_kokoro(text, voice, chunk_path, vtt_chunk_path)
                else:
                    _run_async(_synthesize_edge_tts(text, voice, chunk_path, vtt_chunk_path))
                
                # Verify the file was actually created
                if os.path.exists(chunk_path) and os.path.getsize(chunk_path) > 0:
                    chunk_files.append(chunk_path)
                    with open(vtt_chunk_path, "r", encoding="utf-8") as f:
                        chunk_vtts.append(f.read())
                    break # Success
                else:
                    raise Exception(f"Chunk {i} produced empty file.")
            except Exception as e:
                logger.error(f"Attempt {attempt+1} failed for chunk {i}: {e}")
                if attempt == max_retries - 1:
                    log_path = os.path.join(output_dir, "tts_debug_errors.log")
                    with open(log_path, "a") as dbg_log:
                        dbg_log.write(f"Chunk {i} failed after {max_retries} attempts: {e}\n")
                    raise RuntimeError(f"Audio generation failed for chunk {i+1} after {max_retries} attempts. Engine error: {e}")
                else:
                    time.sleep(2 * (attempt + 1))
        
        # Gentle rate limiting between API calls (not needed for offline engines)
        if engine != "kokoro":
            time.sleep(0.5)

    if not chunk_files:
        logger.warning("No audio chunks were generated. Aborting.")
        return None

    # ── 5. Stitch Audio and Subtitles ─────────────────────────────────────────────
    logger.info(f"Stitching {len(chunk_files)} segments via FFmpeg...")
    list_path = os.path.join(output_dir, "concat_list.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for cf in chunk_files:
            abs_path = os.path.abspath(cf).replace("\\", "/")
            f.write(f"file '{abs_path}'\n")

    final_audio_path = os.path.join(
        StoryManager.DATA_DIR, story_uuid, "generated_audio", f"chapter_{chapter_id}_full.mp3"
    )
    final_vtt_path = os.path.join(
        StoryManager.DATA_DIR, story_uuid, "generated_audio", f"chapter_{chapter_id}_full.vtt"
    )

    # Compile Audio
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
        "-c:a", "libmp3lame", "-q:a", "2", final_audio_path,
    ]

    try:
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"FFmpeg stderr:\n{result.stderr}")
            return None
            
        logger.info(f"Audio compilation successful: {final_audio_path}")
        
        # Compile VTTs
        logger.info("Compiling VTT Subtitles...")
        cumulative_duration = 0.0
        
        with open(final_vtt_path, "w", encoding="utf-8") as f_out:
            f_out.write("WEBVTT\n\n")
            
            for chunk_file, vtt_text in zip(chunk_files, chunk_vtts):
                # Only process the VTT block body (skip WEBVTT header from each chunk)
                vtt_body = "\n".join(vtt_text.split("\n")[2:]).strip()
                if vtt_body:
                    offset_body = offset_vtt_timestamps(vtt_body, cumulative_duration)
                    f_out.write(offset_body + "\n\n")
                    
                # Calculate duration of the chunk to offset the next one
                dur = get_audio_duration(chunk_file)
                cumulative_duration += dur
                
        logger.info(f"VTT compilation successful: {final_vtt_path}")

        return final_audio_path, final_vtt_path
        
    except Exception as e:
        logger.error(f"Final compilation failed: {e}")
        return None
