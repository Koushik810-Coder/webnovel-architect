"""
Extracts all inline SVG diagrams from the webnovel_architect HTML file
and saves them as SVG files. Optionally converts to PNG using cairosvg or Inkscape.
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import re
import os
import sys

html_path = r'c:\Users\WINDOWS\Downloads\webnovel_architect_diagrams_downloadable.html'
out_dir = r'c:\Projects\webnovel-architect\output\diagrams'
os.makedirs(out_dir, exist_ok=True)

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Match each SVG block with its id attribute
pattern = re.compile(r'(<svg\s+id="(d\d+)"[^>]*>.*?</svg>)', re.DOTALL)
svg_blocks = pattern.findall(content)

names = {
    'd1': '01_system_architecture',
    'd2': '02_data_flow',
    'd3': '03_graduation_states',
    'd4': '04_dyg_rag',
    'd5': '05_tts_pipeline',
    'd6': '06_phase_gantt',
}

print(f'Found {len(svg_blocks)} SVG diagrams')

saved_svgs = []
for svg_content, svg_id in svg_blocks:
    name = names.get(svg_id, svg_id)
    # Build a well-formed standalone SVG
    full_svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        + svg_content
    )
    svg_path = os.path.join(out_dir, name + '.svg')
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(full_svg)
    saved_svgs.append((svg_path, name))
    print(f'  [OK] SVG saved: {name}.svg  ({len(svg_content):,} chars)')

# --- Try PNG conversion via cairosvg ---
print('\nAttempting PNG conversion via cairosvg...')
try:
    import cairosvg
    for svg_path, name in saved_svgs:
        png_path = os.path.join(out_dir, name + '.png')
        cairosvg.svg2png(url=svg_path, write_to=png_path, scale=2.0)
        print(f'  [OK] PNG saved: {name}.png')
    print('\nAll done! Files saved to:', out_dir)
    sys.exit(0)
except ImportError:
    print('  cairosvg not installed — trying Inkscape fallback...')

# --- Try PNG conversion via Inkscape (if installed) ---
import subprocess
inkscape_paths = [
    r'C:\Program Files\Inkscape\bin\inkscape.exe',
    r'C:\Program Files (x86)\Inkscape\bin\inkscape.exe',
    'inkscape',
]
inkscape_exe = None
for p in inkscape_paths:
    try:
        result = subprocess.run([p, '--version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            inkscape_exe = p
            break
    except Exception:
        continue

if inkscape_exe:
    for svg_path, name in saved_svgs:
        png_path = os.path.join(out_dir, name + '.png')
        cmd = [inkscape_exe, svg_path, '--export-filename', png_path, '--export-dpi', '192']
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode == 0:
            print(f'  [OK] PNG saved via Inkscape: {name}.png')
        else:
            print(f'  [FAIL] Inkscape failed for {name}: {result.stderr.decode()}')
else:
    print('  Inkscape not found.')
    print('\nSVG files are fully usable. To convert to PNG:')
    print('  pip install cairosvg   (then re-run this script)')
    print('  OR open the SVGs in any browser and print/save as PNG.')

print('\nAll SVG files saved to:', out_dir)
