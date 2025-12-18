
import os
import pygame
import pygame._sdl2.audio as sdl2_audio
import sys

def list_devices(driver_name):
    print(f"\n--- Testing Driver: {driver_name} ---")
    
    # Clean up previous init
    try:
        pygame.quit()
    except:
        pass
        
    if driver_name:
        os.environ["SDL_AUDIODRIVER"] = driver_name
    else:
        if "SDL_AUDIODRIVER" in os.environ:
            del os.environ["SDL_AUDIODRIVER"]

    try:
        pygame.init()
        pygame.mixer.init()
        
        devices = sdl2_audio.get_audio_device_names(False)
        for d in devices:
            print(f"  Found: {d}")
            
    except Exception as e:
        print(f"  Error initializing {driver_name}: {e}")

if __name__ == "__main__":
    # Test Default
    list_devices(None)
    # Test WASAPI
    list_devices("wasapi")
    # Test DirectSound
    list_devices("directsound")
    # Test WinMM
    list_devices("winmm")
