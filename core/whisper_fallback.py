from faster_whisper import WhisperModel
import tempfile
import wave

try:
    model = WhisperModel("base", compute_type="int8")
except Exception as e:
    print("Whisper failed to load:", e)
    model = None

def transcribe_audio(audio_bytes):
    if model is None:
        return ""

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wf = wave.open(f.name, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_bytes)
            wf.close()

            # Force English transcription
            segments, _ = model.transcribe(f.name, language="en", task="transcribe")

            text = ""
            for segment in segments:
                text += segment.text

        return text.strip().lower()

    except Exception as e:
        print("Whisper error:", e)
        return ""