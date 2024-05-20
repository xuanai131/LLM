import os
from typing import Callable
import speech_recognition as sr
import soundfile as sf
import sounddevice as sd
import noisereduce as nr
import librosa
import wave
import struct
import time
import requests
import threading
import signal
from pydub import AudioSegment
import pvporcupine
import urllib
import json
import sys
sys.path.append("../")
import API_keys
import setting
from openai import OpenAI



class VoiceHandle:
    def __init__(self, wake_words: list, 
                 get_chat_response_func: Callable[[str], str]):
        self.sleep_timer = None
        self.wake_words = wake_words
        self.porcupine_wake_words = ['porcupine', 'bumblebee', 'jarvis', 'alexa']
        self.listening_for_wake_word = True
        self._listening_for_query = False
        self._response_generated_by_app = ''
        self._responding_to_user = False
        self.user_query = ''
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
            access_key=API_keys.porcupine_key,
            keywords=self.porcupine_wake_words
        )
    @property
    def listening_for_query(self):
        return self._listening_for_query
    @listening_for_query.setter
    def listening_for_query(self, value):
        if self._listening_for_query != value:
            self._listening_for_query = value
            print('self._listening_for_query: ', self._listening_for_query)
            if self._listening_for_query == True:
                self.play_wav('audio/notification.wav')
                sd.wait()
            self.send_listening_for_query_status()
    @property
    def responding_to_user(self):
        return self._responding_to_user
    @responding_to_user.setter
    def responding_to_user(self, value):
        self._responding_to_user = value
        print('self._responding_to_user: ', self._responding_to_user)
        if value == False:
            self.start_sleep_timer(10)
            self.start_recognizer()
        else:
            self.reset_sleep_timer()
            self.stop_recognizer()
    @property
    def response_generated_by_app(self):
        return self._response_generated_by_app
    @response_generated_by_app.setter
    def response_generated_by_app(self, value):
        self._response_generated_by_app = value
        self.speak(value)
    def send_listening_for_query_status(self, ):
        requests.post(url=setting.IP_ADDRESS+"/listening_for_query", json=({"listening_status": self.listening_for_query}))
    def initial_audio_folder(self, ):
        current_directory = os.getcwd()
        full_path = os.path.join(current_directory, 'audio')
        os.makedirs(full_path, exist_ok=True)
    def start_sleep_timer(self, t=10):
        print('__start_sleep_timer')
        if self.sleep_timer:
            self.sleep_timer.cancel()
        self.sleep_timer = threading.Timer(t, self.enter_sleep_mode)
        self.sleep_timer.start()
    def reset_sleep_timer(self, ):
        print('__reset_sleep_timer')
        if self.sleep_timer:
            self.sleep_timer.cancel()
            self.sleep_timer = None
    def enter_sleep_mode(self, ):
        if self.sleep_timer:
            self.sleep_timer.cancel()
        self.listening_for_query = False
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
    def stt_openai(self, file_name):
        f = sf.SoundFile(file_name)
        if f.frames > 100:
            audio_file= open(file_name, "rb")
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json"
            )
            try:
                no_speech_prob = transcription.segments[0]['no_speech_prob']
            except:
                return None
            print(transcription)
            if no_speech_prob > 0.4:
                return None
            if transcription.language != 'english' and transcription.language != 'vietnamese':
                return None
            text_input = transcription.text
            return text_input
        else:
            return None

    def listen_for_wake_word(self, audio):
        with open(self.wake_detect_file, 'wb') as f:
            f.write(audio.get_wav_data())
        text_input = self.detct_wakeword()
        print('Detected word: ', text_input)
        for wake_word in self.wake_words:
            if wake_word in text_input.lower().strip():
                print('___Assistant: Tôi có thể giúp gì cho bạn?')
                self.listening_for_wake_word = False
                self.listening_for_query = True
                self.responding_to_user = False
                break
    def play_wav(self, file_path):
        data, fs = sf.read(file_path, dtype='float32')
        sd.play(data, fs)
    def reset_audio(self, file):
        with wave.open(file, 'rb') as input_wav:
            params = input_wav.getparams()
            empty_audio_data = b''
            with wave.open(file, 'wb') as output_wav:
                output_wav.setparams(params)
                output_wav.writeframes(empty_audio_data)
    def download_zalo_audio(self, url, filename):
        try_times = 3
        while (try_times>0):
            try :
                with urllib.request.urlopen(url) as response:
                    audio_data = response.read()
                with open(filename, 'wb') as f:
                    f.write(audio_data)
                print("File downloaded successfully as", filename)
                return 
            except:
                try_times = try_times -1
                continue
    def tts_zalo(self, text, filename):
        url = "https://api.zalo.ai/v1/tts/synthesize"
        headers = {
            "apikey": API_keys.zalo_api
        }
        data = {
            "input": text,
            "speaker_id": 3
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            print("Response received:")
            print(response.content)
        else:
            print(f"Request failed with status code {response.status_code}")
            print(response.text)
        json_str = response.content.decode('utf-8')
        url = json.loads(json_str)['data']['url']
        self.download_zalo_audio(url,'test.wav')
    def tts_openai(self, text, filename):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
        )
        response.write_to_file(filename)
    def speak(self, text, ):
        self.responding_to_user = True
        # self.tts_openai(text, self.speak_file)
        self.tts_zalo(text, self.speak_file)
        self.play_wav(self.speak_file)
        def callback_speak():
            sd.wait()
            self.reset_audio(self.wake_detect_file)
            try:
                self.reset_audio(self.prompt_file)
            except:
                pass
            self.responding_to_user = False
            if not self.listening_for_wake_word:
                self.listening_for_query = True
        threading.Thread(target=callback_speak).start()
        
    def GPTResponse(self, audio):
        with open(self.prompt_file, 'wb') as f:
            f.write(audio.get_wav_data())
        prompt_text = self.stt_openai(self.prompt_file)
        self.user_query = prompt_text
        if prompt_text != None:
            self.responding_to_user = True
            requests.post(url=setting.IP_ADDRESS+"/query_voice", json=({"user_query": self.user_query}))
            self.listening_for_query = False
    def callback(self, recognizer, audio):
        print('_______________Call back: ', end='')
        if self.listening_for_wake_word:
           self.listen_for_wake_word(audio)
        else:
            if not self.responding_to_user:
                self.user_query = ''
                self.GPTResponse(audio)
    def stop_recognizer(self, ):
        print('__stop recognizer..........')
        self.stop_listening(wait_for_stop=False)
    def start_recognizer(self, ):
        print('__start recognizer..........')
        if self.stop_listening:
            self.stop_listening(wait_for_stop=False)
        self.source = sr.Microphone()
        with self.source as s:
            self.recognizer.adjust_for_ambient_noise(s, duration=1)
        self.stop_listening = self.recognizer.listen_in_background(self.source, self.callback)
    def run(self, ):
        def signal_handler(sig, frame):
            if self.stop_listening:
                self.stop_listening(wait_for_stop=False)
            print('\nExiting gracefully...')
            sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)
        self.recognizer = sr.Recognizer()
        self.source = sr.Microphone()
        with self.source as s:
            self.recognizer.adjust_for_ambient_noise(s, duration=1)
        self.stop_listening =  self.recognizer.listen_in_background(self.source, self.callback)
        print('\nSay one of ', self.wake_words, 'to wake me up. \n')
    def reset_all(self, ):
        self.reset_audio(self.wake_detect_file)
        self.reset_audio(self.prompt_file)
        self.responding_to_user = False
        self.enter_sleep_mode()