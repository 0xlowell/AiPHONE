import websocket
import json
import base64
from pygame import mixer
import time
import os

# Initialize pygame mixer
mixer.init(44100, -16, 1, 2048)

def on_message(ws, message):
    try:
        data = json.loads(message)
        if data["type"] == "audio.delta":
            print("Received audio chunk")
            
            # Save and play audio
            audio_data = base64.b64decode(data["delta"])
            temp_file = "temp_response.wav"
            
            with open(temp_file, "wb") as f:
                f.write(audio_data)
            
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
        print(f"Error processing message: {e}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

def on_open(ws):
    print("WebSocket connection opened")

def main():
    ws = websocket.WebSocketApp(
        "ws://localhost:8765",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    
    ws.run_forever()

if __name__ == "__main__":
    main() 