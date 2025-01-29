import os
import json
import websocket
import base64
import pyaudio
import pygame
import threading
from dotenv import load_dotenv
import logging
from datetime import datetime
import wave
import io

# Configuration simple des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'openai_realtime_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

# Chargement de la clé API
load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    logging.error("Pas de clé API trouvée dans .env")
    exit(1)

# Configuration audio améliorée
CHUNK = 4096  # Buffer plus grand pour éviter les saccades
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 24000

# Dossier pour les enregistrements
RECORDINGS_DIR = "recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)

def create_wav_file_object(audio_data):
    """Crée un fichier WAV en mémoire à partir des données audio brutes."""
    wav_file = io.BytesIO()
    with wave.open(wav_file, 'wb') as wavfile:
        wavfile.setnchannels(CHANNELS)
        wavfile.setsampwidth(2)  # 16-bit audio
        wavfile.setframerate(RATE)
        wavfile.writeframes(audio_data)
    wav_file.seek(0)
    return wav_file

def save_audio(audio_data, prefix="openai"):
    """Sauvegarde l'audio dans un fichier WAV."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{RECORDINGS_DIR}/{prefix}_{timestamp}.wav"
    
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(RATE)
        wf.writeframes(audio_data)
    logging.info(f"Audio sauvegardé: {filename}")

def on_message(ws, message):
    try:
        data = json.loads(message)
        
        if data["type"] == "response.audio.delta":
            # Sauvegarde l'audio d'OpenAI
            audio_data = base64.b64decode(data["delta"])
            save_audio(audio_data, "openai")
            
            # Joue l'audio
            pygame.mixer.stop()
            wav_file = create_wav_file_object(audio_data)
            sound = pygame.mixer.Sound(wav_file)
            sound.play()
            
        elif data["type"] == "response.text.delta":
            print(data.get('delta', ''), end='', flush=True)
            
    except Exception as e:
        logging.error(f"Erreur message: {str(e)}")

def on_error(ws, error):
    logging.error(f"Erreur WebSocket: {str(error)}")

def on_close(ws, status, message):
    logging.info("Connexion fermée")

def on_open(ws):
    logging.info("Connecté")
    
    # Configuration initiale
    ws.send(json.dumps({
        "type": "session.update",
        "session": {
            "modalities": ["text", "audio"],
            "voice": "shimmer",
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {"model": "whisper-1"}
        }
    }))
    
    # Démarrage de l'audio
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    def audio_sender():
        try:
            while ws.sock and ws.sock.connected:
                data = stream.read(CHUNK, exception_on_overflow=False)
                # Sauvegarde l'audio de l'utilisateur
                save_audio(data, "user")
                
                ws.send(json.dumps({
                    "type": "input_audio_buffer.append",
                    "audio": base64.b64encode(data).decode('utf-8')
                }))
        except Exception as e:
            logging.error(f"Erreur audio: {str(e)}")
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()
    
    threading.Thread(target=audio_sender, daemon=True).start()

def main():
    # Initialisation de pygame avec un buffer plus grand
    pygame.mixer.init(
        frequency=RATE,
        size=-16,
        channels=CHANNELS,
        buffer=4096
    )
    pygame.mixer.set_num_channels(1)  # Force un seul canal audio
    
    # Connexion WebSocket
    ws = websocket.WebSocketApp(
        "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview",
        header=[
            f"Authorization: Bearer {API_KEY}",
            "OpenAI-Beta: realtime=v1"
        ],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    ws.run_forever()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Arrêt manuel")
    except Exception as e:
        logging.error(f"Erreur: {str(e)}")