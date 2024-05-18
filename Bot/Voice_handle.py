import os
import speech_recognition as sr
import soundfile as sf
import sounddevice as sd
import noisereduce as nr
import librosa
import wave
import struct
import time
import threading
from pydub import AudioSegment
import pvporcupine
import sys
sys.path.append("../")
import API_keys
from API_keys import *
from openai import OpenAI



class VoiceHandle:
    def __init__(self, wake_words: list, get_chat_response_func):
        self.sleep_timer = None
        self.wake_words = wake_words
        self.porcupine_wake_words = ['porcupine', 'bumblebee', 'jarvis', 'alexa']
        self.listening_for_wake_word = True
        self.responding_to_user = False
        self.get_chat_response = get_chat_response_func
        self.initial_audio_folder()
        self.wake_detect_file = 'audio/wake_detect.wav'
        self.wake_detect_16000_file = 'audio/wake_detect_16000.wav'
        self.wake_detect_16000_removenoises_file = 'audio/wake_detect_16000_removenoises.wav'
        self.prompt_file = 'audio/prompt.wav'
        self.speak_file = 'audio/speak.mp3'

        self.client = OpenAI()
        self.recognizer = None
        self.source = None
        self.stop_listening = None
        self.porcupine = pvporcupine.create(
            access_key=porcupine_key,
            keywords=self.porcupine_wake_words
        )
        
    def initial_audio_folder(self, ):
        current_directory = os.getcwd()
        full_path = os.path.join(current_directory, 'audio')
        os.makedirs(full_path, exist_ok=True)
    def start_sleep_timer(self, ):
        if self.sleep_timer:
            self.sleep_timer.cancel()
        self.sleep_timer = threading.Timer(10, self.enter_sleep_mode)
        self.sleep_timer.start()
    def reset_sleep_timer(self, ):
        if self.sleep_timer:
            self.sleep_timer.cancel()
            self.sleep_timer = None
    def enter_sleep_mode(self, ):
        self.listening_for_wake_word = True
        print(f"Entered sleep mode. Say one of {self.wake_words} to activate.")
    def read_file(self, file_name, sample_rate):
        wav_file = wave.open(file_name, mode="rb")
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        num_frames = wav_file.getnframes()

        if wav_file.getframerate() != sample_rate:
            raise ValueError("Audio file should have a sample rate of %d. got %d" % (sample_rate, wav_file.getframerate()))
        if sample_width != 2:
            raise ValueError("Audio file should be 16-bit. got %d" % sample_width)
        if channels == 2:
            print("Picovoice processes single-channel audio but stereo file is provided. Processing left channel only.")
        samples = wav_file.readframes(num_frames)
        wav_file.close()
        frames = struct.unpack('h' * num_frames * channels, samples)
        return frames[::channels]
    def remove_noises(self, input_file, output_file):
        audio_data, sr = librosa.load(input_file, sr=None)
        sample_rate = 16000
        reduced_noise = nr.reduce_noise(y=audio_data, sr=sample_rate)
        sf.write(output_file, reduced_noise, sample_rate)
    def detct_wakeword(self, ):
        # Convert 44100Hz audio to 16000Hz
        audio = AudioSegment.from_wav(self.wake_detect_file)
        audio = audio.set_frame_rate(16000)
        audio.export(self.wake_detect_16000_file, format="wav")
        # Remove noises from audio
        self.remove_noises(self.wake_detect_16000_file, self.wake_detect_16000_removenoises_file)
        # Read file and detect wake word
        audio = self.read_file(self.wake_detect_16000_removenoises_file, 16000)
        num_frames = len(audio) // self.porcupine.frame_length
        for i in range(num_frames):
            frame = audio[i * self.porcupine.frame_length:(i + 1) * self.porcupine.frame_length]
            result = self.porcupine.process(frame)
            if result >= 0:
                wakeword = self.porcupine_wake_words[result]
                return wakeword
            else:
                wakeword = str(result)
        return wakeword
    def stt(self, file_name):
        # print('_check file size')
        f = sf.SoundFile(file_name)
        if f.frames > 100:
            # i += 1
            # with open(f'audio/wake_detect_{i}.wav', 'wb') as f:
            #     f.write(audio.get_wav_data())
            # print('_convert speech to text\r')
            # t = time.time()
            audio_file= open(file_name, "rb")
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            text_input = transcription.text
            # print('   ', time.time()-t)
            return text_input
        else:
            return None

    def listen_for_wake_word(self, audio):
        with open(self.wake_detect_file, 'wb') as f:
            f.write(audio.get_wav_data())
        # text_input = self.stt(self.wake_detect_file)
        text_input = self.detct_wakeword()
        print('Detected word: ', text_input)
        for wake_word in self.wake_words:
            if wake_word in text_input.lower().strip():
                print('___Assistant: Tôi có thể giúp gì cho bạn?')
                self.speak('Tôi có thể giúp gì cho bạn')
                # speak('Listening')
                self.listening_for_wake_word = False
                break
    def play_wav(self, file_path):
        data, fs = sf.read(file_path, dtype='float32')
        sd.play(data, fs)
        sd.wait()
    def reset_audio(self, file):
        with wave.open(file, 'rb') as input_wav:
            params = input_wav.getparams()
            empty_audio_data = b''
            with wave.open(file, 'wb') as output_wav:
                output_wav.setparams(params)
                output_wav.writeframes(empty_audio_data)
    def speak(self, text):
        # print('set responding_to_user to True')
        self.responding_to_user = True
        self.stop_recognizer()
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
        )

        response.write_to_file(self.speak_file)
        self.play_wav(self.speak_file)
        self.reset_audio(self.wake_detect_file)
        try:
            self.reset_audio(self.prompt_file)
        except:
            pass
        self.start_recognizer()
        # print('set responding_to_user to False')
        self.responding_to_user = False
    def GPTResponse(self, audio):
        try:
            with open(self.prompt_file, 'wb') as f:
                f.write(audio.get_wav_data())
            prompt_text = self.stt(self.prompt_file)
            if len(prompt_text.strip()) == 0:
                print('Empty prompt. Please speak again.')
                self.speak('Empty prompt. Please speak again.')
                self.listening_for_wake_word = True
            else:
                print('_____User: ' + prompt_text)
                output = self.get_chat_response(prompt_text)
                print('___Assistant: ', output)
                self.speak(output)
        except Exception as e:
            print('Prompt error: ', e)
    def callback(self, recognizer, audio):
        print('_______________Call back')
        if self.listening_for_wake_word:
           self.listen_for_wake_word(audio)
        else:
            if not self.responding_to_user:
                self.reset_sleep_timer()
                self.GPTResponse(audio)
                self.start_sleep_timer()
    def stop_recognizer(self, ):
        self.stop_listening(wait_for_stop=False)
        # source.__exit__(None, None, None)
    def start_recognizer(self, ):
        self.source = sr.Microphone()
        with self.source as s:
            self.recognizer.adjust_for_ambient_noise(s, duration=1)
        self.stop_listening = self.recognizer.listen_in_background(self.source, self.callback)
    def run(self, ):
        self.recognizer = sr.Recognizer()
        self.source = sr.Microphone()
        with self.source as s:
            self.recognizer.adjust_for_ambient_noise(s, duration=1)
        self.stop_listening =  self.recognizer.listen_in_background(self.source, self.callback)
        print('\nSay one of ', self.wake_words, 'to wake me up. \n')
        while True:
            time.sleep(0.5)
    def reset_all(self, ):
        self.reset_audio(self.wake_detect_file)
        self.reset_audio(self.prompt_file)
        self.reset_sleep_timer()
        self.stop_recognizer()
        self.start_recognizer()