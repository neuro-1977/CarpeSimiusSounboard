from comtypes import CoInitialize, CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import comtypes.client

# Constants
eCapture = 1
eConsole = 0

def test_mic_control():
    try:
        CoInitialize()
        
        # This will generate the comtypes.gen.Mmdevapi module
        enumerator = comtypes.client.CreateObject(
            "{BCDE0395-E52F-467C-8E3D-C4579291692E}", 
            interface=comtypes.gen.Mmdevapi.IMMDeviceEnumerator
        )
        
        # Get Default Capture Device (Microphone)
        mic_device = enumerator.GetDefaultAudioEndpoint(eCapture, eConsole)
        
        # Activate Volume Interface
        interface = mic_device.Activate(
            "{5CDF2C82-841E-4546-9722-0CF74078229A}", # IID_IAudioEndpointVolume
            CLSCTX_ALL,
            None
        )
        
        from ctypes import cast, POINTER
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        # Check current state
        current_mute = volume.GetMute()
        print(f"Current Mic Mute State: {current_mute}")
        
        # Toggle
        new_state = 1 if current_mute == 0 else 0
        volume.SetMute(new_state, None)
        print(f"Toggled Mic Mute to: {new_state}")
        
        # Verify
        print(f"Verification: {volume.GetMute()}")
        
        # Toggle back
        volume.SetMute(current_mute, None)
        print(f"Restored Mic Mute to: {current_mute}")
        
    except Exception as e:
        print(f"Error: {e}")
        # import traceback
        # traceback.print_exc()

if __name__ == "__main__":
    # Force generation of the module first if needed
    try:
        comtypes.client.GetModule("mmdevapi.dll")
    except:
        pass
        
    test_mic_control()