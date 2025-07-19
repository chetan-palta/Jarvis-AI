import os
import queue
import json
import pyaudio
import sounddevice as sd
print(sd.query_devices())

import vosk
import pyttsx3
import webbrowser
from gtts import gTTS
import pygame
import google.generativeai as genai


# Initialize Gemini
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[
    {"role": "user", "parts": ["You are Jarvis, a concise virtual assistant. Keep responses under 2 sentences unless specifically asked for details. You can control apps, play music, and answer questions"]},
    {"role": "model", "parts": ["Understood. I'm Jarvis, ready to assist with brief, focused responses"]}
])

# Voice engine setup
engine = pyttsx3.init()

# Load Vosk model
model_path = r"C:\Users\itzch\Downloads\vosk-model-small-en-us-0.15 (1)\vosk-model-small-en-us-0.15"
if not os.path.exists(model_path):
    print("Vosk model path is incorrect.")
    exit()
recognizer = vosk.Model(model_path)

# Speak function
def speak(text):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save('temp.mp3')
        pygame.mixer.init()
        pygame.mixer.music.load('temp.mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        os.remove("temp.mp3")
    except Exception as e:
        print(f"TTS Error: {e}")

# Listen using PyAudio + Vosk
def listen():
    q = queue.Queue()
    
    def callback(in_data, frame_count, time_info, status):
        q.put(in_data)
        return (None, pyaudio.paContinue)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=1,  # 👈 change this to the index from step 1
                frames_per_buffer=8000,
                stream_callback=callback)

    rec = vosk.KaldiRecognizer(recognizer, 16000)

    print("🎤 Listening for a command...")
    stream.start_stream()

    while True:
        data = q.get()
        print("🔊 Captured audio bytes:", len(data))  # Debug
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "").strip()
            if text:
                print(f"✅ Recognized: {text}")
                stream.stop_stream()
                stream.close()
                p.terminate()
                return text.lower()

# Process commands
def processCommand(command):
    if "open google" in command:
        webbrowser.open("https://google.com")
    elif "youtube" in command:
        webbrowser.open("https://youtube.com")
    elif "exit" in command or "stop" in command:
        speak("Goodbye!")
        exit()
    else:
        response = chat.send_message(command)
        speak(response.text)

# Main loop
if __name__ == "__main__":
    speak("Jarvis initialized. How can I help you?")
    
    while True:
        try:
            command = listen()
            if not command:
                command = input("Couldn't hear. Type your command: ")
            processCommand(command)
        except Exception as e:
            print(f"An error occurred: {e}")

