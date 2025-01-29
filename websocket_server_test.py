import asyncio
import websockets
import base64
import wave
import struct
import time
import json

async def audio_stream(websocket):
    print("Client connected")
    
    # Create a simple beep sound
    def create_beep():
        duration = 0.5  # seconds
        sample_rate = 44100
        frequency = 440  # Hz
        
        samples = []
        for i in range(int(sample_rate * duration)):
            sample = 32767 * 0.3 * float(i % frequency < frequency/2)
            samples.append(struct.pack('h', int(sample)))
        
        # Create WAV in memory
        audio_data = b''
        with wave.open('temp.wav', 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b''.join(samples))
        
        with open('temp.wav', 'rb') as f:
            audio_data = f.read()
        
        return base64.b64encode(audio_data).decode('utf-8')

    try:
        while True:
            # Send a beep every 2 seconds
            audio_base64 = create_beep()
            await websocket.send(json.dumps({
                "type": "audio.delta",
                "delta": audio_base64
            }))
            await asyncio.sleep(2)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def main():
    async with websockets.serve(audio_stream, "localhost", 8765):
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main()) 