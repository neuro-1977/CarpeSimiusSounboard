
import pygame
import pygame._sdl2.audio as sdl2_audio
import sys

try:
    pygame.init()
    pygame.mixer.init()
    
    print(f"Pygame Version: {pygame.version.ver}")
    print(f"SDL Version: {pygame.get_sdl_version()}")

    print("\n--- Audio Devices ---")
    devices = sdl2_audio.get_audio_device_names(False) # False for output devices
    for d in devices:
        print(f"Output: {d}")

    inputs = sdl2_audio.get_audio_device_names(True) # True for input
    for d in inputs:
        print(f"Input: {d}")

    print("\nSUCCESS: Device listing works.")
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

pygame.quit()
