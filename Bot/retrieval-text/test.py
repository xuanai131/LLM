import os
from pocketsphinx import Decoder, Config
import pvporcupine
import sys
sys.path.append("../")
from API_keys import *
wake_words = ['porcupine', 'bumblebee', 'jarvis', 'alexa']
porcupine = pvporcupine.create(
  access_key=porcupine_key,
  keywords=wake_words
)
porcupine_wake_words = ['porcupine', 'bumblebee', 'jarvis', 'alexa']

import struct
import wave
def read_file(file_name, sample_rate):
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


audio_file_path = 'audio/wake_detect_16000_removenoises.wav'
audio = read_file(audio_file_path, 16000)
# keywords = list()
# audio_file_path = 'audio/wake_detect.wav'

# for x in keyword_paths:
#     keyword_phrase_part = os.path.basename(x).replace('.ppn', '').split('_')
#     if len(keyword_phrase_part) > 6:
#         keywords.append(' '.join(keyword_phrase_part[0:-6]))
#     else:
#         keywords.append(keyword_phrase_part[0])

num_frames = len(audio) // porcupine.frame_length
for i in range(num_frames):
    frame = audio[i * porcupine.frame_length:(i + 1) * porcupine.frame_length]
    result = porcupine.process(frame)
    if result >= 0:
        print(porcupine_wake_words[result])
    else:
        print(str(result))