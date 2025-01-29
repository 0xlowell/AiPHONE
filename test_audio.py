import websocket
import json
import base64
from pygame import mixer
import time
import os
import wave
import struct

# Initialize pygame mixer
mixer.init(44100, -16, 2, 2048)

def create_test_wav():
    """Create a simple WAV file with a beep sound"""
    sampleRate = 44100
    duration = 0.5  # seconds
    frequency = 440  # Hz (A4 note)
    
    # Generate samples
    samples = []
    for i in range(int(sampleRate * duration)):
        sample = 32767 * 0.3 * float(i % frequency < frequency/2)
        samples.append(struct.pack('h', int(sample)))
    
    # Write WAV file
    with wave.open('test_output.wav', 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sampleRate)
        wav_file.writeframes(b''.join(samples))
    
    # Read the file and encode to base64
    with open('test_output.wav', 'rb') as wav_file:
        return base64.b64encode(wav_file.read()).decode('utf-8')

def play_audio(audio_data):
    try:
        # Save base64 audio to temporary file
        temp_file = "test_output.wav"
        with open(temp_file, "wb") as f:
            f.write(base64.b64decode(audio_data))
        
        print("Playing audio...")
        mixer.music.load(temp_file)
        mixer.music.play()
        
        # Wait for audio to finish
        while mixer.music.get_busy():
            time.sleep(0.1)
            
        # Cleanup
        mixer.music.unload()
        os.remove(temp_file)
        print("Audio playback completed")
        
    except Exception as e:
        print(f"Error playing audio: {e}")

def test_audio_playback():
    print("Starting audio test...")
    audio_base64 = create_test_wav()
    play_audio(audio_base64)
    print("Test completed")

if __name__ == "__main__":
    test_audio_playback() 