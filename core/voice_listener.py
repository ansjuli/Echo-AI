import sounddevice as sd
import queue
import json
from core.command_executor import execute_command
from core.whisper_fallback import transcribe_audio
from vosk import Model, KaldiRecognizer

q = queue.Queue()
last_audio = b""

# Load commands
with open("commands.json", "r", encoding="utf-8") as f:
    COMMANDS = json.load(f)

model = Model("models/vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

def callback(indata, frames, time, status):
    global last_audio
    if status:
        print(status)
    last_audio = bytes(indata)
    q.put(bytes(indata))

def listen_forever():
    print("Echo Hybrid Listening... 🎧")
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if not text:
                    continue
                print(f"Heard (Vosk): {text}")

                success = execute_command(text)

                if not success:
                    print("Fallback to Whisper...")
                    whisper_text = transcribe_audio(last_audio)
                    if whisper_text:
                        print(f"Heard (Whisper): {whisper_text}")
                        execute_command(whisper_text)
                    else:
                        print("Whisper failed or empty result")