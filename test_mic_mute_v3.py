
from pycaw.utils import AudioUtilities
from pycaw.api.endpointvolume import IAudioEndpointVolume
import comtypes

def test_simple():
    try:
        # 1. Get Mic
        mic = AudioUtilities.GetMicrophone()
        
        # 2. Activate IAudioEndpointVolume
        # IAudioEndpointVolume._iid_ is defined in pycaw
        interface = mic.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
        
        # 3. Cast/Query
        volume = interface.QueryInterface(IAudioEndpointVolume)
        
        # 4. Test
        curr = volume.GetMute()
        print(f"Start Mute: {curr}")
        
        volume.SetMute(1, None)
        print(f"Muted: {volume.GetMute()}")
        
        volume.SetMute(0, None)
        print(f"Unmuted: {volume.GetMute()}")
        
        # Restore
        volume.SetMute(curr, None)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    comtypes.CoInitialize()
    test_simple()
