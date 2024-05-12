import pyaudio
import wave
import audioop
import os
from pydub import AudioSegment
import time
import matplotlib.pyplot as plt
import numpy as np
from openai import OpenAI

def convert_wav_to_mp3(wav_file, mp3_file):
    # Load the WAV file
    audio = AudioSegment.from_wav(wav_file)
    
    # Export as MP3
    audio.export(mp3_file, format="mp3")
    print(f"Audio converted to {mp3_file}")
class Voice_Record:
    def __init__(self):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100  
        self.threshold = 750
        self.max_silent_frames = 80
        self.recorded_audio_path = "recorded_audio.mp3"
        self.timeout = 10
    def visualize_audio(self, waveform):
        if not hasattr(self, 'fig'):
            plt.ion()  # Turn on interactive mode for plotting
            self.fig, self.ax = plt.subplots()
            self.x = np.arange(0, len(waveform))
            self.line, = self.ax.plot(self.x, waveform)
            self.ax.set_ylim(-5000, 5000)                              
        else:
            self.line.set_ydata(waveform)
            self.ax.relim()
            self.ax.autoscale_view()
            plt.draw()
            plt.pause(0.0001)
    def record(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk)
        
        print("Recording...")

        frames = []
        silent_frames = 0
        recording = False
        start_time = time.time()
        while True:
            data = stream.read(self.chunk)
            rms = audioop.rms(data, 2)
            stop_time = time.time()
            if(stop_time-start_time)> self.timeout:
                break
            if rms > self.threshold:
                silent_frames = 0
                if not recording:
                    print("Recording started.")
                    recording = True
            else:
                if recording:
                    print(silent_frames)
                    silent_frames += 1
                    if silent_frames > self.max_silent_frames:
                        print("Recording stopped.")
                        break

            if recording:
                frames.append(data)
                # waveform = np.frombuffer(data, dtype=np.int16)
                # self.visualize_audio(waveform)
                

        stream.stop_stream()
        stream.close()
        p.terminate()

        self.save_audio(frames)

    def save_audio(self, frames):
        if frames:
            with wave.open(self.recorded_audio_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))
            print(f"Audio saved as {self.recorded_audio_path}")
        else:
            print("No audio recorded.")
    def speech_to_text(self):
        client = OpenAI()
        audio_file= open("recorded_audio.mp3", "rb")
        transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file,
        language="vi")
        return transcription.text