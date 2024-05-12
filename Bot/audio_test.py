# Use a pipeline as a high-level helper
from transformers import pipeline
import time

pipe = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-large")

output = pipe('recorded_audio.mp3')['text']
print(output)