import sounddevice as sd
import queue
import vosk
import json
import pyttsx3

model_path = "C:/Users/itzch/Downloads/vosk-model-small-en-us-0.15 (1)/vosk-model-small-en-us-0.15"
model = vosk.Model(model_path)

# Queue to collect audio data
q = queue.Queue()

# Configure TTS
engine = pyttsx3.init()
engine.setProperty("rate", 170)

# Callback for audio input
def callback(indata, frames, time, status):
    if status:
        print("⚠️", status)
    q.put(bytes(indata))

# Start stream with correct mic index
device_index = 1  # your working mic index
samplerate = 16000
with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device_index,
                       dtype='int16', channels=1, callback=callback):
    print("🎤 Listening for a command...")

    rec = vosk.KaldiRecognizer(model, samplerate)

    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "").lower()
            if text:
                print(f"🗣 You said: {text}")
                
                # Add your custom commands here
                if "time" in text:
                    import datetime
                    now = datetime.datetime.now().strftime("%I:%M %p")
                    reply = f"The time is {now}"
                    print(f"🧠 Jarvis: {reply}")
                    engine.say(reply)
                    engine.runAndWait()
                elif "exit" in text or "quit" in text:
                    print("👋 Exiting...")
                    break
                else:
                    reply = "Sorry, I didn't understand that."
                    print(f"🧠 Jarvis: {reply}")
                    engine.say(reply)
                    engine.runAndWait()
        else:
            # You can see partial results here if needed
            pass
