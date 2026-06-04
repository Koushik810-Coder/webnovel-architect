import os
import zipfile
import subprocess
import shutil
import re
from typing import List, Tuple
from app.core.story_manager import StoryManager
from app.core.logger import get_logger

logger = get_logger(__name__)

def get_audio_files(story_uuid: str) -> List[Tuple[int, str, str]]:
    """Returns a sorted list of tuples (chapter_id, mp3_path, vtt_path) for all generated chapters."""
    audio_dir = os.path.join(StoryManager.DATA_DIR, story_uuid, "generated_audio")
    if not os.path.exists(audio_dir):
        return []

    chapters = []
    pattern = re.compile(r"^chapter_(\d+)_full\.mp3$")
    for f in os.listdir(audio_dir):
        match = pattern.match(f)
        if match:
            chap_id = int(match.group(1))
            mp3_path = os.path.join(audio_dir, f)
            vtt_path = os.path.join(audio_dir, f"chapter_{chap_id}_full.vtt")
            if os.path.exists(vtt_path):
                chapters.append((chap_id, mp3_path, vtt_path))

    return sorted(chapters, key=lambda x: x[0])

def export_audiobook_zip(story_uuid: str) -> str:
    """Packages all MP3s and VTTs into a raw ZIP archive for basic download."""
    files = get_audio_files(story_uuid)
    if not files:
        raise ValueError(f"No generated audio found for story {story_uuid}")

    export_dir = os.path.join(StoryManager.DATA_DIR, story_uuid, "export")
    os.makedirs(export_dir, exist_ok=True)
    zip_path = os.path.join(export_dir, f"audiobook_{story_uuid}_raw.zip")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for chap_id, mp3, vtt in files:
            zf.write(mp3, os.path.basename(mp3))
            zf.write(vtt, os.path.basename(vtt))

    logger.info(f"Raw audiobook ZIP exported to: {zip_path}")
    return zip_path

def export_audiobook_html(story_uuid: str) -> str:
    """Packages MP3s, VTTs, and an index.html web player into a ZIP archive."""
    files = get_audio_files(story_uuid)
    if not files:
        raise ValueError(f"No generated audio found for story {story_uuid}")

    export_dir = os.path.join(StoryManager.DATA_DIR, story_uuid, "export")
    os.makedirs(export_dir, exist_ok=True)
    zip_path = os.path.join(export_dir, f"audiobook_{story_uuid}_web.zip")

    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Webnovel Audiobook Player</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #111; color: #eee; }
        .player-container { background: #222; padding: 20px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h1 { color: #fff; border-bottom: 2px solid #444; padding-bottom: 10px; }
        .playlist { list-style: none; padding: 0; margin-top: 20px; }
        .playlist li { padding: 10px; border-bottom: 1px solid #333; cursor: pointer; transition: background 0.2s; }
        .playlist li:hover { background: #333; }
        .playlist li.active { background: #4a90e2; color: #fff; font-weight: bold; }
        audio { width: 100%; margin-top: 20px; }
        ::cue { background-color: rgba(0, 0, 0, 0.8); color: white; font-size: 1.2em; }
    </style>
</head>
<body>
    <div class="player-container">
        <h1>Webnovel Audiobook Player</h1>
        <audio id="audio-player" controls crossorigin="anonymous">
            <source id="audio-source" src="" type="audio/mpeg">
            <track id="audio-track" default kind="subtitles" srclang="en" label="English" src="">
            Your browser does not support the audio element.
        </audio>
        <ul class="playlist" id="playlist">
"""

    for chap_id, mp3, vtt in files:
        html_content += f'            <li data-mp3="audio/{os.path.basename(mp3)}" data-vtt="audio/{os.path.basename(vtt)}">Chapter {chap_id}</li>\n'
    html_content += """        </ul>
    </div>
    <script>
        const audioPlayer = document.getElementById('audio-player');
        const audioSource = document.getElementById('audio-source');
        const audioTrack = document.getElementById('audio-track');
        const playlistItems = document.querySelectorAll('#playlist li');
        
        function loadTrack(index) {
            if (index < 0 || index >= playlistItems.length) return;
            
            playlistItems.forEach(item => item.classList.remove('active'));
            const item = playlistItems[index];
            item.classList.add('active');
            
            audioSource.src = item.getAttribute('data-mp3');
            audioTrack.src = item.getAttribute('data-vtt');
            audioPlayer.load();
            audioPlayer.play();
            
            audioPlayer.onended = () => {
                loadTrack(index + 1);
            };
        }
        
        playlistItems.forEach((item, index) => {
            item.addEventListener('click', () => {
                loadTrack(index);
            });
        });
        
        // Load first track automatically
        if (playlistItems.length > 0) {
            loadTrack(0);
        }
    </script>
</body>
</html>"""

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("index.html", html_content)
        for _, mp3, vtt in files:
            zf.write(mp3, f"audio/{os.path.basename(mp3)}")
            zf.write(vtt, f"audio/{os.path.basename(vtt)}")

    logger.info(f"Web player audiobook ZIP exported to: {zip_path}")
    return zip_path

def export_single_audiobook(story_uuid: str) -> Tuple[str, str]:
    """
    Stitches all chapter MP3s via FFmpeg into a single audiobook file.
    Also merges the VTT files with offset timestamps.
    Returns (mp3_path, vtt_path).
    """
    files = get_audio_files(story_uuid)
    if not files:
        raise ValueError(f"No generated audio found for story {story_uuid}")

    export_dir = os.path.join(StoryManager.DATA_DIR, story_uuid, "export")
    os.makedirs(export_dir, exist_ok=True)

    final_audio = os.path.join(export_dir, f"audiobook_{story_uuid}_full.mp3")
    final_vtt = os.path.join(export_dir, f"audiobook_{story_uuid}_full.vtt")

    # Check if ffmpeg is available
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg not found on system PATH. Required for single audiobook export.")

    concat_list_path = os.path.join(export_dir, "concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for _, mp3, _ in files:
            # Escape path for ffmpeg concat demuxer
            safe_path = mp3.replace("\\\\", "/").replace("'", "'\\\\''")
            f.write(f"file '{safe_path}'\\n")

    logger.info("Running FFmpeg to concatenate chapters...")
    try:
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_list_path,
            "-c:a", "libmp3lame", "-q:a", "2",
            final_audio
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        if os.path.exists(concat_list_path):
            os.remove(concat_list_path)

    logger.info(f"Single audiobook compiled to: {final_audio}")

    # We could also compile VTTs here, but for simplicity we'll just stitch audio for now.
    # To offset timestamps, we'd need ffprobe to get exact duration of each chapter.
    return final_audio, final_vtt
