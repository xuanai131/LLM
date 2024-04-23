from flask import Flask
from flask import render_template
import sys
from flask import request,Response,redirect, url_for,jsonify
from urllib.parse import urlparse
import cv2
import base64
import numpy as np
import time
import threading
from flask_socketio import SocketIO
import requests 
import os 
from openai import OpenAI
import soundfile as sf
import sounddevice as sd
import multiprocessing
import urllib.request
import subaudio
camera = cv2.VideoCapture(0)

sys.path.append("../Bot")
import book_search
import Helper_Utilities
from langchain_core.messages import HumanMessage, AIMessage
import voice_record
image_queue = []
lock = threading.Lock()
new_frame_event = threading.Event()
OpenAIHistoryConversation = []
graph = Helper_Utilities.CreateGraph(OpenAIHistoryConversation)
DoRecord = voice_record.Voice_Record()
sys.path.append("database")
import book_search
import setting
app = Flask(__name__)
socketio = SocketIO(app)
response = ""
response_tool = ""
camera_st = False
voice_st = False
user_input_st = False
user_input_message = ""


def play_wav(file_path):
    data, fs = sf.read(file_path, dtype='float32')
    sd.play(data, fs)
    sd.wait()

@app.route("/")
def hello_world():
    return render_template('index.html',camera_state=camera_st)

def LoadBookCovers(book_ids):
    images = []
    for book_id in book_ids:
        images.append("data:image/jpeg;base64," + str(book_search.search_book_image_by_id(book_id)[0]))
    return images
def use_open_ai_audio(data):
    client = OpenAI()

    response = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input=data,
)
    response.write_to_file('audio.wav')
    play_wav('audio.wav')
    # response.stream_to_file
def download_audio_in_web(url, filename):
    try:
        response = requests.get(url, stream=True)
        print("Status code:", response.status_code)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print("Audio file downloaded successfully as:", filename)
            play_wav(filename)
        else:
            print("Failed to download audio file")
    except Exception as e:
        print("An error occurred:", e)
def text_to_speech(url,filename):
    try_times = 3
    while (try_times>0):
        try :
            download_zalo_audio(url,filename)
            return 
        except:
            try_times = try_times -1
            continue
def download_zalo_audio(url,filename):
# Open the URL and read the content
    with urllib.request.urlopen(url) as response:
        audio_data = response.read()
# Write the content to a file
    with open(filename, 'wb') as f:
        f.write(audio_data)

    print("File downloaded successfully as", filename)
    # play_wav(filename)
    subaudio.run()

@app.route("/image", methods=["GET","POST"])
def get_image():
    global image_of_book
    if request.method == 'POST':
        msg = request.get_json()
        print("MSG", type(msg['id']))
        image_of_book = msg['id'][1:-1].split(',');
        print(image_of_book)
        print(type(image_of_book))

        images = LoadBookCovers(image_of_book)
        print(type(images[0]))
        # return render_template('index.html')
        socketio.emit('book_images', {'visible': True, 'image' : images})
        return image_of_book
        # video_feed_url = url_for('image')
        # return render_template('index.html', video_feed_url = "response")
    else:
        socketio.emit('book_images', {'visible': False, 'image' : images})
        return image_of_book
@app.route("/user_input_mess",methods = ["POST","GET"])
def get_message_user_tool():
    global user_input_message
    if request.method == 'POST':
        data = request.form.get("msg")
        print("/user input message posted ",data)
        # message = data["message"]
        user_input_message = data
        # socketio.emit('user_input_message',{"message":message})
        return "posted data."
    else:
        return  str(user_input_message)
@app.route("/user_input_state",methods = ["POST","GET"])
def get_user_input_state():
    global user_input_st
    global user_input_message
    if request.method == 'POST':
        data = request.get_json()  
        print("/user input state posted ",data)
        if data and "input_st" in data:
            state = data["input_st"]
            user_input_st = state
            socketio.emit('user_input_state',{"state":state})
            if (state == True):
                while(user_input_message == ""):
                    continue
                result = user_input_message
                user_input_message = ""
                return result
            else:
                return "state is false"
        else:
            return "Invalid JSON data."
    else:
        return str(user_input_st)
    
@app.route("/return_form",methods = ["POST","GET"])
def return_form():
    if request.method == 'POST':
        data = request.get_json()  
        # print('//////////////////', data['message'])
        if data['message'] == 'start':
            socketio.emit('return_form_visiblity', {'visible': True})
        else:
            socketio.emit('return_form_visiblity', {'visible': False})
        return data
@app.route("/student-book_info",methods = ["POST","GET"])
def student_book_info():
    if request.method == 'POST':
        data = request.get_json()  
        socketio.emit('student-book_info_socket', data)
        return ''
@app.route("/borrow_book_student_info",methods = ["POST","GET"])
def return_student_info():
    if request.method == 'POST':
        data = request.get_json()  
        socketio.emit('return_student_info_socket', data)
        return ''
@app.route("/tool_action", methods=["POST","GET"])
def chat_from_tool():
    global response_tool
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request
        if data and "message" in data:
            msg = data["message"]
            if msg:
                t = time.localtime(time.time())
                
                response_tool = msg
                socketio.emit('update_html', {'data': response_tool,"time": str(t.tm_hour)+ " "+ str(t.tm_min) + " "+str(t.tm_sec)})
                return response 
            else:
                return  "No message received."
        else:
            return "Invalid JSON data."
    else:
        return  str(response_tool)


@app.route("/get", methods=["GET","POST"])
def chat():
    global response
    # response = ""
    
    if request.method == 'POST':
        msg = request.form.get("msg")
        if msg:
            response = get_Chat_response(msg)
            return response
        else:
            return "No message received."
    else:
        return response


def get_Chat_response(text):
    query = HumanMessage(text)
    OpenAIHistoryConversation.append(query)
    inputs = {
        # "history" : [],
        "messages": OpenAIHistoryConversation
    }
    
    for s in graph.stream(inputs):
        if "__end__" not in s:
            print(s)
        else:
            print("-------------------------------------")
            print(s)
            try:
                answer = AIMessage(s.get('__end__')['messages'][-1].content)
                print("-------------------------------------")
                print(answer)
            except:
                pass
    OpenAIHistoryConversation.append(answer)
    
    return answer.content

def generate_frames(image_data):
    global count
    if not image_data:
        print("Received empty image data")
        return None

    try:
        # Decode received image from base64
        image_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)

        if np_arr.size == 0:
            print("Received corrupted image data")
            return

        # Decode image using OpenCV
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        # count += 1
        # cv2.imwrite(f'images/image_{count}.jpg', frame)

        # Convert frame to jpeg format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        return frame

        # yield (b'--frame\r\n'
        #        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    except Exception as e:
        print("Error decoding image:", e)
@app.route('/voice_status', methods=['POST','GET'])
def voice_status_update():
    global voice_st
    if request.method == 'POST':
        data = request.get_json().get('voice_status')
        print(str(data))
        if (str(data) == "True"):
            voice_st = True
            DoRecord.record()
            res = DoRecord.speech_to_text()
            print(res)
            # socketio.emit(('message_in_voice', {'message': res}))
            return res
        else:
            voice_st = False
            # socketio.emit('container_visibility_change', {'visible': False})
        return 'voice received'
    else:
        socketio.emit(('message_in_voice', {'message': 'voice off'}))
        return str(voice_st)

@app.route('/camera_status', methods=['POST','GET'])
def camera_status_update():
    global camera_st
    if request.method == 'POST':
        data = request.form['camera_status']
        print(str(data))
        if (str(data) == "True"):
            camera_st = True
            socketio.emit('container_visibility_change', {'visible': True})
        else:
            camera_st = False
            socketio.emit('container_visibility_change', {'visible': False})
        return 'Image received'
    else:
        return str(camera_st)


@app.route('/camera', methods=['POST'])
def camera():
    global image_queue
    
    image_data = request.form['image_base64']
    frame = generate_frames(image_data)
    if frame is not None:
        image_queue.append(frame)
    new_frame_event.set()
    return 'Image received'

def generate():
    global image_queue
    while True:
        new_frame_event.wait()  # Wait for new frames
        new_frame_event.clear()  # Reset event
        while image_queue:
            with lock:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + image_queue.pop(0) + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/download_audio', methods=['POST'])
def download_audio_from_url():
    data = request.get_json().get('url')
    # print("the url in front end side :",data)
    # data = "https://chunk.lab.zalo.ai/a745e9c971a198ffc1b0/a745e9c971a198ffc1b0/"
    # download_audio_in_web(data,'audio.wav')
    # data = request.get_json().get('data')
    # text_to_speech(data,'audio.wav')
    audio_thread = threading.Thread(target=text_to_speech, args=(data,'audio.wav'))
    audio_thread.start()
    audio_thread.join()
    return "success"
if __name__ == '__main__':
    host = setting.IP if len(setting.IP) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5001
    socketio.run(app, host=host, port=port)





