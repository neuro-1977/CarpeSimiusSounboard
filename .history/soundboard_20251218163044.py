import os
import sys
import threading
import pygame
import webview
from pathlib import Path

# ------------------------------------------------------------------
# Determine the base directory (works for script and frozen .exe)
# ------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

SOUNDS_DIR = BASE_DIR
LOGO_PATH = BASE_DIR / "logo.png"
FAVICON_PATH = BASE_DIR / "favicon.ico"

EXTENSIONS = {".mp3", ".wav", ".ogg"}

# ------------------------------------------------------------------
# pygame init in background thread
# ------------------------------------------------------------------
def init_pygame():
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

threading.Thread(target=init_pygame, daemon=True).start()

# ------------------------------------------------------------------
# Build HTML with logo and favicon
# ------------------------------------------------------------------
logo_html = ""
if LOGO_PATH.exists():
    logo_html = f'<img src="file://{LOGO_PATH.resolve()}" style="max-width:300px; height:auto; margin:20px 0;">'

favicon_html = ""
if FAVICON_PATH.exists():
    favicon_html = f'<link rel="icon" href="file://{FAVICON_PATH.resolve()}">'

html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    {favicon_html}
    <title>Local Soundboard</title>
    <style>
        body {{
            background: #1e1e1e;
            color: #fff;
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            text-align: center;
        }}
        .logo-container {{
            margin-bottom: 20px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 16px;
            max-width: 1200px;
            margin: 0 auto;
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
    <div class="logo-container">
        {logo_html}
        <h1>My Local Soundboard</h1>
    </div>
    <div id="grid" class="grid"></div>
    <div id="nosounds" class="no-sounds" style="display:none;">
        No sound files found in the app folder.<br>
        Put some .mp3, .wav or .ogg files here and restart.
    </div>

    <script>
        function playSound(filename) {{
            pywebview.api.play_sound(filename);
        }}

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
# API for JavaScript
# ------------------------------------------------------------------
class Api:
    def get_sounds(self):
        sounds = []
        for file in SOUNDS_DIR.iterdir():
            if file.is_file() and file.suffix.lower() in EXTENSIONS:
                sounds.append({
                    "name": file.stem.replace("_", " ").title(),
                    "path": str(file.resolve())
                })
        sounds.sort(key=lambda x: x["name"])
        return sounds

    def play_sound(self, filepath):
        def _play():
            try:
                sound = pygame.mixer.Sound(filepath)
                sound.play()
                while pygame.mixer.get_busy():
                    pygame.time.wait(100)
            except Exception as e:
                print(f"Error playing {filepath}: {e}")
        threading.Thread(target=_play, daemon=True).start()

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main():
    api = Api()
    icon_path = str(FAVICON_PATH) if FAVICON_PATH.exists() else None

    webview.create_window(
        "Local Soundboard",
        html=html,
        js_api=api,
        width=1000,
        height=800,
        resizable=True,
        background_color='#1e1e1e'
    )
    webview.start(icon=icon_path)  # Sets window icon where supported (GTK/Qt); fallback to exe icon on Windows

if __name__ == '__main__':
    main()