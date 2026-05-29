from email.mime import audio
import threading
import sys
import time
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import wave
import speech_recognition as sr
from speech_recognition import AudioData

stop_event = threading.Event()

def wait_for_enter():
    input("\nPress Enter to stop recording...\n")
    stop_event.set()

def spinner():
    chars = '|/-\\'
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f'\rRecording...  + {chars[i % 4]}')
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    print("\nRecording complete.")

def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    frames = []

    threading.Thread(target=wait_for_enter, daemon=True).start()
    threading.Thread(target=spinner, daemon=True).start()

    while not stop_event.is_set():
        frames.append(stream.read(1024))

    stream.stop_stream()
    stream.close()
    width = p.get_sample_size(pyaudio.paInt16)
    p.terminate()
    audio_data = b''.join(frames), width, 16000
    return audio_data

def save_audio(data, rate, width, filename='recording.wav'):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(width)
        wf.setframerate(rate)
        wf.writeframes(data)
    print(f"Audio saved to {filename}")

def transcribe_audio(data, rate, width):
    recognizer = sr.Recognizer()
    audio_data = AudioData(data, rate, width)
    try:
        text = recognizer.recognize_google(audio_data)
        print("Transcription: " + text)
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

def plot_waveform(data, rate):
    samples = np.frombuffer(data, dtype=np.int16)
    time_axis = np.linspace(0, len(samples) / rate, num=len(samples))
    plt.figure(figsize=(10, 4))
    plt.plot(time_axis, samples, color='blue')
    plt.title("Audio Waveform")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def main():
    print("=" * 40)
    print("HELLO AI, CAN U HEARC ME?")
    print("=" * 40)
    print("\nSpeak into the microphone. Press Enter to stop recording.\n")

    audio_data, width, rate = record_audio()
    save_audio(audio_data, rate, width)
    transcribe_audio(audio_data, rate, width)
    plot_waveform(audio_data, rate)

if __name__ == "__main__":
    main()