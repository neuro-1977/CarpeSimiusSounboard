import os
import sys
import threading
import pygame
import webview
from pathlib import Path

# ------------------------------------------------------------------
# Determine the folder where the executable/script is located
# ------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    # Running as compiled .exe
    BASE_DIR = Path(sys.executable).parent
else:
    # Running as script
    BASE_DIR = Path(__file__).parent

SOUNDS_DIR = BASE_DIR  # All MP3/WAV files in this folder will be used

# Supported extensions
EXTENSIONS = {".mp3", ".wav", ".ogg"}

# ------------------------------------------------------------------
# pygame mixer init (runs in background thread)
# ------------------------------------------------------------------
def init_pygame():
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

threading.Thread(target=init_pygame, daemon=True).start()

# ------------------------------------------------------------------
# HTML UI
# ------------------------------------------------------------------
html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Local Soundboard</title>
    <style>
        body {{
            background: #1e1e1e;
            color: #fff;
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 30px;
            color: #00ffaa;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 16px;
        }}
        button {{
            padding: 20px;
            font-size: 16px;
            background: #333;
            color: white;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s;
            word-wrap: break-word;
        }}
        button:hover {{
            background: #555;
            transform: scale(1.05);
        }}
        button:active {{
            background: #00ffaa;
            color: black;
        }}
        .no-sounds {{
            text-align: center;
            font-size: 20px;
            color: #888;
            margin-top: 100px;
        }}
    </style>
</head>
<body>
    <h1>My Local Soundboard</h1>
    <div id="grid" class="grid"></div>
    <div id="nosounds" class="no-sounds" style="display:none;">No sound files found in the app folder.<br>Put some .mp3 or .wav files here and restart.</div>

    <script>
        function playSound(filename) {{
            // This calls back into Python
            pywebview.api.play_sound(filename);
        }}

        // Populate buttons
        window.addEventListener('pywebviewready', function() {{
            pywebview.api.get_sounds().then(function(sounds) {{
                const grid = document.getElementById('grid');
                const nosounds = document.getElementById('nosounds');
                if (sounds.length === 0) {{
                    nosounds.style.display = 'block';
                    return;
                }}
                sounds.forEach(sound => {{
                    const btn = document.createElement('button');
                    btn.textContent = sound.name;
                    btn.onclick = () => playSound(sound.path);
                    grid.appendChild(btn);
                }});
            }});
        }});
    </script>
</body>
</html>
"""

# ------------------------------------------------------------------
# Python API exposed to JavaScript
# ------------------------------------------------------------------
class Api:
    def get_sounds(self):
        sounds = []
        for file in SOUNDS_DIR.iterdir():
            if file.is_file() and file.suffix.lower() in EXTENSIONS:
                sounds.append({
                    "name": file.stem.replace("_", " ").title(),  # nicer button text
                    "path": str(file)
                })
        # Sort alphabetically
        sounds.sort(key=lambda x: x["name"])
        return sounds

    def play_sound(self, filepath):
        def _play():
            try:
                sound = pygame.mixer.Sound(filepath)
                sound.play()
                # Optional: wait until finished (so overlapping is limited)
                while pygame.mixer.get_busy():
                    pygame.time.wait(100)
            except Exception as e:
                print(f"Error playing {filepath}: {e}")
        # Play in separate thread so UI doesn't freeze
        threading.Thread(target=_play, daemon=True).start()

# ------------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------------
def main():
    api = Api()
    # Create window (native look, no browser frame)
    webview.create_window(
        "Local Soundboard",
        html=html,
        js_api=api,
        width=900,
        height=700,
        resizable=True,
        minimized=False,
        background_color='#1e1e1e'
    )
    webview.start()

if __name__ == '__main__':
    main()