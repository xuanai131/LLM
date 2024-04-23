from transformers import pipeline
import time
transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-small")
start_time  = time.time()
output = transcriber("/var/www/html/flask/recorded_audio.mp3")['text']
end_time = time.time()
print(output ,  end_time-start_time)