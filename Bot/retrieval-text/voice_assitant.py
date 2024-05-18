from os import system
import speech_recognition as sr
import soundfile as sf
import sounddevice as sd
import wave
import time
import threading
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import sys
sys.path.append("../")
import API_keys
from openai import OpenAI
client = OpenAI()
i = 0

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
function_def = {
    "name": "route",
    "description": "trả lời câu hỏi của người dùng",
    "parameters": {
        "title": "routeSchema",
        "type": "object",
        "properties": {
            "messages": {
                "title": "messages",
                "ouput": 'text',
            }
        },
        "required": ["messages"],
    },
}
system_assistant_prompt = (
    "Bạn là một trợ lí robot thông minh phục vụ trong thư viện HCMUTE, bạn tên là Librarios. Bạn là một robot di động có 2 bánh xe giúp bạn có thể đi lại tự do trong thư viện, "
    "nhờ đó bạn có thể dẫn người dùng đến nơi để những cuốn sách mà sinh viên hay giảng viên mong muốn."
    "Lưu ý: chỉ trả lời những câu hỏi bằng tiếng việt và có nghĩa, nếu không hãy phản hồi là bạn không hiểu câu hỏi."
)

assistant_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_assistant_prompt),
        # MessagesPlaceholder(variable_name="history"),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

assistant_chain = (
    assistant_prompt
    | llm.bind_functions(functions=[function_def], function_call="route")
    | JsonOutputFunctionsParser()
)



sleep_timer = None
wake_word = 'porcupine'
listening_for_wake_word = True
responding_to_user = False

def start_sleep_timer():
    global sleep_timer, listening_for_wake_word
    if sleep_timer:
        sleep_timer.cancel()
    sleep_timer = threading.Timer(10, enter_sleep_mode)
    sleep_timer.start()
def reset_sleep_timer():
    global sleep_timer
    if sleep_timer:
        sleep_timer.cancel()
        sleep_timer = None
def enter_sleep_mode():
    global listening_for_wake_word
    listening_for_wake_word = True
    print(f"Entered sleep mode. Say the {wake_word} to activate.")

def listen_for_wake_word(audio):
    # print('/////////////////////////', len(audio.frames))
    global listening_for_wake_word, i
    with open('wake_detect.wav', 'wb') as f:
        f.write(audio.get_wav_data())
    f = sf.SoundFile('wake_detect.wav')
    if f.frames > 100:
        # i += 1
        # with open(f'audio/wake_detect_{i}.wav', 'wb') as f:
        #     f.write(audio.get_wav_data())
        audio_file= open('wake_detect.wav', "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        text_input = transcription.text
        print('/////////////////////////////////', text_input)
        if wake_word in text_input.lower().strip():
            print('___Assistant: Tôi có thể giúp gì cho bạn?')
            speak('Tôi có thể giúp gì cho bạn')
            # speak('Listening')
            listening_for_wake_word = False
def play_wav(file_path):
    data, fs = sf.read(file_path, dtype='float32')
    sd.play(data, fs)
    sd.wait()
def reset_audio(file):
    with wave.open(file, 'rb') as input_wav:
        params = input_wav.getparams()
        empty_audio_data = b''
        with wave.open(file, 'wb') as output_wav:
            output_wav.setparams(params)
            output_wav.writeframes(empty_audio_data)
def speak(text):
    global responding_to_user
    print('set responding_to_user to True')
    responding_to_user = True
    stop_recognizer()
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )

    response.write_to_file("speak.mp3")
    play_wav("speak.mp3")
    reset_audio('wake_detect.wav')
    reset_audio('prompt.wav')
    start_recognizer()
    print('set responding_to_user to False')
    responding_to_user = False
def GPTResponse(audio):
    global listening_for_wake_word
    try:
        with open('prompt.wav', 'wb') as f:
            f.write(audio.get_wav_data())
        f = sf.SoundFile('prompt.wav')
        if f.frames > 100:
            audio_file= open('prompt.wav', "rb")
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            prompt_text = transcription.text
            if len(prompt_text.strip()) == 0:
                print('Empty prompt. Please speak again.')
                speak('Empty prompt. Please speak again.')
                listening_for_wake_word = True
            else:
                print('_____User: ' + prompt_text)
                output = assistant_chain.invoke([HumanMessage(prompt_text)])['messages'][0]
                print('___Assistant: ', output)
                speak(output)
    except Exception as e:
        print('Prompt error: ', e)
def callback(recognizer, audio):
    global listening_for_wake_word, responding_to_user
    if listening_for_wake_word:
        listen_for_wake_word(audio)
    else:
        if not responding_to_user:
            reset_sleep_timer()
            GPTResponse(audio)
            start_sleep_timer()
source, r = None, None
def stop_recognizer():
    global source, stop_listening
    stop_listening(wait_for_stop=False)
    # source.__exit__(None, None, None)
def start_recognizer():
    global source, r,stop_listening
    source = sr.Microphone()
    with source as s:
        r.adjust_for_ambient_noise(s, duration=1)
    stop_listening = r.listen_in_background(source, callback)



r = sr.Recognizer()
source = sr.Microphone()
with source as s:
    r.adjust_for_ambient_noise(s, duration=1)
stop_listening = r.listen_in_background(source, callback)
print('\nSay', wake_word, 'to wake me up. \n')
while True:
    time.sleep(1)