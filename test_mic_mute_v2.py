
from pycaw.utils import AudioUtilities
from pycaw.interfaces.endpointvolume import IAudioEndpointVolume
from ctypes import cast, POINTER
import comtypes
from comtypes import CLSCTX_ALL

def test_mic_control_simple():
    try:
        comtypes.CoInitialize()
        
        # 1. Get the enumerator using pycaw's internal helper if available, 
        # but let's just use the fact that AudioUtilities imports comtypes
        
        # Let's try to get all devices and find the default input
        # This is inefficient but avoids the GetDefaultAudioEndpoint direct call if wrappers are broken
        
        # ...Actually, let's just fix the comtypes generation
        # comtypes.client.GetModule("mmdevapi.dll") usually fixes it.
        
        import comtypes.client
        # This is the type lib for MMDevice API
        comtypes.client.GetModule("mmdevapi.dll") 
        
        enumerator = comtypes.client.CreateObject(
            "{BCDE0395-E52F-467C-8E3D-C4579291692E}", 
            comtypes.gen.Mmdevapi.IMMDeviceEnumerator,
            CLSCTX_ALL
        )
        
        # eCapture = 1, eConsole = 0
        mic = enumerator.GetDefaultAudioEndpoint(1, 0)
        
        interface = mic.Activate(
            "{5CDF2C82-841E-4546-9722-0CF74078229A}", 
            CLSCTX_ALL, 
            None
        )
        
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        print(f"Current Mute: {volume.GetMute()}")
        
        volume.SetMute(1, None)
        print("Muted.")
        
        volume.SetMute(0, None)
        print("Unmuted.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_mic_control_simple()
