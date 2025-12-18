import sys
import os
import pygame
import pygame._sdl2.audio as sdl2_audio
from pathlib import Path
import comtypes
from pycaw.utils import AudioUtilities
from pycaw.api.endpointvolume import IAudioEndpointVolume
import webbrowser
import urllib.request
import zipfile
import tempfile
import threading
import ctypes
import time

# ------------------------------------------------------------------
# Configuration & Assets
# ------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    EXE_DIR = Path(sys.executable).parent
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    EXE_DIR = Path(__file__).parent
    BUNDLE_DIR = Path(__file__).parent

SOUNDS_DIR = EXE_DIR / "sounds"
LOGO_PATH = BUNDLE_DIR / "logo.png"
ICON_PATH = BUNDLE_DIR / "favicon.ico"

# Colors
C_BG = (30, 30, 30)
C_BTN = (50, 50, 50)
C_BTN_HOVER = (70, 70, 70)
C_BTN_ACTIVE = (0, 200, 150)
C_TEXT = (255, 255, 255)
C_DANGER = (200, 60, 60)
C_SAFE = (60, 200, 60)
C_ACCENT = (60, 100, 200)
C_MODAL_BG = (40, 40, 40)
C_MODAL_OVERLAY = (0, 0, 0, 200)

EXTS = {".mp3", ".wav", ".ogg"}

class DriverInstaller:
    def __init__(self):
        self.status = "Ready"
        self.is_working = False
        self.is_done = False
        self.error = None
        
    def start_install(self):
        if self.is_working: return
        self.is_working = True
        self.is_done = False
        self.error = None
        threading.Thread(target=self._install_thread, daemon=True).start()
        
    def _install_thread(self):
        try:
            url = "https://download.vb-audio.com/Download_CABLE/VBCABLE_Driver_Pack43.zip"
            
            self.status = "Downloading Driver (1/3)..."
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "cable_driver.zip")
            urllib.request.urlretrieve(url, zip_path)
            
            self.status = "Extracting Files (2/3)..."
            extract_dir = os.path.join(temp_dir, "extracted")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                
            setup_exe = "VBCABLE_Setup_x64.exe"
            exe_path = os.path.join(extract_dir, setup_exe)
            
            if not os.path.exists(exe_path):
                for root, dirs, files in os.walk(extract_dir):
                    if setup_exe in files:
                        exe_path = os.path.join(root, setup_exe)
                        break
            
            if not os.path.exists(exe_path):
                raise Exception("Installer executable not found.")

            self.status = "Launching Setup (3/3)..."
            time.sleep(1)
            
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe_path, None, os.path.dirname(exe_path), 1)
            if ret <= 32:
                raise Exception(f"Failed to launch installer (Code {ret})")
            
            self.status = "Please complete the setup wizard."
            self.is_done = True
            
        except Exception as e:
            self.error = str(e)
            self.status = "Error Occurred."
            print(f"Install Error: {e}")
        finally:
            self.is_working = False

class MicController:
    def __init__(self):
        self.vol_iface = None
        self.init_interface()

    def init_interface(self):
        try:
            mic = AudioUtilities.GetMicrophone()
            if mic:
                iface = mic.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
                self.vol_iface = iface.QueryInterface(IAudioEndpointVolume)
            else:
                self.vol_iface = None
        except:
            self.vol_iface = None

    def toggle(self):
        if not self.vol_iface: self.init_interface()
        if self.vol_iface:
            try:
                curr = self.vol_iface.GetMute()
                self.vol_iface.SetMute(not curr, None)
                return not curr
            except:
                self.init_interface()
        return False

    def is_muted(self):
        if not self.vol_iface:
            self.init_interface()
            if not self.vol_iface: return False
        try:
            return bool(self.vol_iface.GetMute())
        except:
            self.init_interface()
            return False

class Button:
    def __init__(self, rect, text, callback, color=C_BTN, hover_color=C_BTN_HOVER):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.cb = callback
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.active_timer = 0

    def draw(self, surface, font):
        col = C_BTN_ACTIVE if self.active_timer > 0 else (self.hover_color if self.is_hovered else self.color)
        if self.active_timer > 0: self.active_timer -= 1
        
        pygame.draw.rect(surface, col, self.rect, border_radius=8)
        
        # Word Wrap
        words = self.text.split(' ')
        lines = []
        curr = []
        for w in words:
            if font.size(' '.join(curr + [w]))[0] < self.rect.width - 20:
                curr.append(w)
            else:
                lines.append(' '.join(curr))
                curr = [w]
        lines.append(' '.join(curr))

        h = len(lines) * font.get_linesize()
        y = self.rect.centery - h / 2
        for line in lines:
            t = font.render(line, True, C_TEXT)
            surface.blit(t, t.get_rect(centerx=self.rect.centerx, top=y))
            y += font.get_linesize()

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            self.active_timer = 10
            if self.cb: self.cb()
            return True
        return False

class Dropdown:
    def __init__(self, x, y, w, h, font, options, on_select):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.options = options
        self.on_select = on_select
        self.is_open = False
        self.sel_idx = 0
        self.hov_idx = -1

    def set_options(self, options, default=None):
        self.options = options
        self.sel_idx = options.index(default) if default in options else 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_open:
                list_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, len(self.options) * self.rect.height)
                if list_rect.collidepoint(event.pos):
                    idx = (event.pos[1] - self.rect.bottom) // self.rect.height
                    if 0 <= idx < len(self.options):
                        self.sel_idx = idx
                        self.is_open = False
                        if self.on_select: self.on_select(self.options[idx])
                    return True
                self.is_open = False
                if self.rect.collidepoint(event.pos): return True
            elif self.rect.collidepoint(event.pos):
                self.is_open = True
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.is_open:
                list_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, len(self.options) * self.rect.height)
                self.hov_idx = (event.pos[1] - self.rect.bottom) // self.rect.height if list_rect.collidepoint(event.pos) else -1
            else:
                self.hov_idx = -1
        return self.is_open and self.rect.inflate(0, len(self.options)*self.rect.height).collidepoint(pygame.mouse.get_pos())

    def draw(self, surface):
        pygame.draw.rect(surface, C_BTN, self.rect, border_radius=5)
        pygame.draw.rect(surface, (100,100,100), self.rect, 1, border_radius=5)
        
        txt = self.options[self.sel_idx] if 0 <= self.sel_idx < len(self.options) else "No Devices"
        if len(txt) > 28: txt = txt[:25] + "..."
        t = self.font.render(txt, True, C_TEXT)
        surface.blit(t, (self.rect.x + 10, self.rect.centery - t.get_height()//2))
        
        # Arrow
        pygame.draw.polygon(surface, (200,200,200), [(self.rect.right-20, self.rect.centery-2), (self.rect.right-10, self.rect.centery-2), (self.rect.right-15, self.rect.centery+3)])

        if self.is_open:
            for i, opt in enumerate(self.options):
                r = pygame.Rect(self.rect.x, self.rect.bottom + i*self.rect.height, self.rect.width, self.rect.height)
                col = C_ACCENT if i == self.sel_idx else (C_BTN_HOVER if i == self.hov_idx else (40,40,40))
                pygame.draw.rect(surface, col, r)
                pygame.draw.rect(surface, (60,60,60), r, 1)
                
                if len(opt) > 28: opt = opt[:25] + "..."
                t = self.font.render(opt, True, (220,220,220))
                surface.blit(t, (r.x + 10, r.centery - t.get_height()//2))

class Modal:
    def __init__(self, w, h, font, installer):
        self.w, self.h, self.font, self.inst = w, h, font, installer
        self.rect, self.btn_rect, self.link_rect = None, None, None

    def draw(self, surface, sw, sh):
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill(C_MODAL_OVERLAY)
        surface.blit(overlay, (0,0))

        cx, cy = sw//2, sh//2
        self.rect = pygame.Rect(cx - self.w//2, cy - self.h//2, self.w, self.h)
        pygame.draw.rect(surface, C_MODAL_BG, self.rect, border_radius=12)
        pygame.draw.rect(surface, C_ACCENT, self.rect, 2, border_radius=12)

        h_font = pygame.font.SysFont("Segoe UI", 24, bold=True)
        
        def draw_text(txt, y, col=C_TEXT, font=self.font):
            t = font.render(txt, True, col)
            surface.blit(t, (self.rect.centerx - t.get_width()//2, self.rect.y + y))

        if self.inst.is_working:
            draw_text("INSTALLING...", 40, C_TEXT, h_font)
            draw_text(self.inst.status, self.h//2, (200,200,200))
            self.btn_rect = None
            return

        if self.inst.is_done:
            draw_text("REBOOT REQUIRED", 40, C_SAFE, h_font)
            msgs = ["Installer launched.", "1. Follow wizard.", "2. RESTART PC.", "3. Open app & select CABLE."]
            for i, m in enumerate(msgs): draw_text(m, 100 + i*30)
            
            self.btn_rect = pygame.Rect(self.rect.centerx-60, self.rect.bottom-60, 120, 40)
            pygame.draw.rect(surface, C_BTN, self.btn_rect, border_radius=8)
            t = self.font.render("CLOSE", True, C_TEXT)
            surface.blit(t, t.get_rect(center=self.btn_rect.center))
            return

        if self.inst.error:
            draw_text("ERROR", 40, C_DANGER, h_font)
            draw_text(str(self.inst.error)[:40], self.h//2, C_DANGER)
            self.btn_rect = pygame.Rect(self.rect.centerx-60, self.rect.bottom-60, 120, 40)
            pygame.draw.rect(surface, C_BTN, self.btn_rect, border_radius=8)
            t = self.font.render("CLOSE", True, C_TEXT)
            surface.blit(t, t.get_rect(center=self.btn_rect.center))
            return

        draw_text("MISSING AUDIO DRIVER", 40, C_DANGER, h_font)
        msgs = ["App needs VB-CABLE to use mic.", "", "We can install it for you."]
        for i, m in enumerate(msgs): draw_text(m, 90 + i*30)

        self.btn_rect = pygame.Rect(self.rect.centerx-100, self.rect.bottom-80, 200, 50)
        col = C_BTN_HOVER if self.btn_rect.collidepoint(pygame.mouse.get_pos()) else C_ACCENT
        pygame.draw.rect(surface, col, self.btn_rect, border_radius=8)
        t = self.font.render("INSTALL DRIVER", True, C_TEXT)
        surface.blit(t, t.get_rect(center=self.btn_rect.center))

    def handle_event(self, event, close_cb):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_rect and self.btn_rect.collidepoint(event.pos):
                if self.inst.is_done or self.inst.error: close_cb()
                else: self.inst.start_install()
                return True
            if self.rect and self.rect.collidepoint(event.pos): return True
        return False

class Soundboard:
    def __init__(self):
        try: comtypes.CoInitialize()
        except: pass
        self.mic_ctrl = MicController()
        pygame.init()
        
        self.screen = pygame.display.set_mode((1000, 800), pygame.RESIZABLE)
        pygame.display.set_caption("Carpe Simius Soundboard")
        if LOGO_PATH.exists():
            try: pygame.display.set_icon(pygame.image.load(str(LOGO_PATH)))
            except: pass

        self.font = pygame.font.SysFont("Segoe UI", 18)
        self.s_font = pygame.font.SysFont("Segoe UI", 14)
        self.clock = pygame.time.Clock()
        self.running = True
        self.mic_muted = self.mic_ctrl.is_muted()
        self.poll_t = 0
        self.devs = self.get_devices()
        self.curr_dev = None
        self.init_mixer(None)
        
        self.dd = Dropdown(20, 20, 220, 30, self.s_font, self.devs, self.on_dev_sel)
        self.dd.set_options(self.devs, self.curr_dev)
        self.inst = DriverInstaller()
        self.modal = Modal(500, 400, self.font, self.inst)
        
        self.show_help = not any("cable" in d.lower() or "virtual" in d.lower() for d in self.devs)
        self.sounds, self.buttons = [], []
        self.refresh()

    def refresh(self):
        self.sounds = []
        if SOUNDS_DIR.exists():
            for f in SOUNDS_DIR.iterdir():
                if f.suffix.lower() in EXTS:
                    self.sounds.append({"name": f.stem.replace("_", " ").title(), "path": str(f.resolve())})
        self.sounds.sort(key=lambda x: x["name"])
        self.devs = self.get_devices()
        self.dd.set_options(self.devs, self.curr_dev)
        self.layout()

    def layout(self):
        self.buttons = []
        w, h = self.screen.get_size()
        cols = max(1, (w - 40) // 215)
        for i, s in enumerate(self.sounds):
            r = i // cols
            c = i % cols
            rect = (20 + c*215, 150 + r*115, 200, 100)
            self.buttons.append(Button(rect, s["name"], lambda p=s["path"]: self.play(p)))

    def play(self, path):
        try: pygame.mixer.Sound(path).play()
        except: pass

    def on_dev_sel(self, name): self.init_mixer(name)

    def get_devices(self):
        try: return sdl2_audio.get_audio_device_names(False) or ["System Default"]
        except: return ["System Default"]

    def init_mixer(self, name):
        if pygame.mixer.get_init(): pygame.mixer.quit()
        try:
            target = name if name else None
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512, devicename=target)
            self.curr_dev = target if target else "System Default"
        except:
            if name: self.init_mixer(None)

    def run(self):
        while self.running:
            w, h = self.screen.get_size()
            self.poll_t += 1
            if self.poll_t > 30:
                self.poll_t = 0
                self.mic_muted = self.mic_ctrl.is_muted()

            for e in pygame.event.get():
                if e.type == pygame.QUIT: self.running = False
                elif e.type == pygame.VIDEORESIZE: self.layout()
                
                if self.show_help:
                    if self.modal.handle_event(e, lambda: setattr(self, 'show_help', False)): continue
                    continue
                if self.dd.handle_event(e): continue 

                if e.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = e.pos
                    if w-160 <= mx <= w-20 and 20 <= my <= 50:
                        self.mic_ctrl.toggle()
                        self.mic_muted = self.mic_ctrl.is_muted()
                    elif 260 <= mx <= 360 and 20 <= my <= 50: self.refresh()
                    elif w-330 <= mx <= w-290 and 20 <= my <= 50: self.show_help = True

                for b in self.buttons: b.handle_event(e)

            self.screen.fill(C_BG)
            
            # Refresh Btn
            rr = pygame.Rect(260, 20, 100, 30)
            col = C_BTN_HOVER if rr.collidepoint(pygame.mouse.get_pos()) else C_BTN
            pygame.draw.rect(self.screen, col, rr, border_radius=5)
            t = self.s_font.render("Refresh", True, C_TEXT)
            self.screen.blit(t, t.get_rect(center=rr.center))

            # Help Btn
            hr = pygame.Rect(w-330, 20, 40, 30)
            col = C_ACCENT if hr.collidepoint(pygame.mouse.get_pos()) else C_BTN
            pygame.draw.rect(self.screen, col, hr, border_radius=5)
            t = self.s_font.render("?", True, C_TEXT)
            self.screen.blit(t, t.get_rect(center=hr.center))

            # Mic Btn
            mr = pygame.Rect(w-160, 20, 140, 30)
            col = C_DANGER if self.mic_muted else (C_SAFE if not mr.collidepoint(pygame.mouse.get_pos()) else (80,220,80))
            pygame.draw.rect(self.screen, col, mr, border_radius=5)
            t = self.s_font.render("MIC MUTED" if self.mic_muted else "MIC ACTIVE", True, C_TEXT if self.mic_muted else (20,20,20))
            self.screen.blit(t, t.get_rect(center=mr.center))
            
            for b in self.buttons: b.draw(self.screen, self.font)
            
            if not self.buttons:
                t = self.font.render("No sounds found in 'sounds/' folder.", True, (150,150,150))
                self.screen.blit(t, (w//2 - t.get_width()//2, h//2))

            self.dd.draw(self.screen)
            if self.show_help: self.modal.draw(self.screen, w, h)

            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    Soundboard().run()