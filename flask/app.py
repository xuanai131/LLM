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
import re
import json
camera = cv2.VideoCapture(0)
from colorama import Fore, Back, Style
sys.path.append("../Bot")
from Database_handle import *
from Global_variable import *
import Helper_Utilities
from langchain_core.messages import HumanMessage, AIMessage
import voice_record
import barcode
from barcode.writer import ImageWriter
from PIL import Image
from io import BytesIO
import base64
import uuid
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

image_queue = []
lock = threading.Lock()
new_frame_event = threading.Event()
OpenAIHistoryConversation = []
graph = Helper_Utilities.CreateGraph(OpenAIHistoryConversation)
DoRecord = voice_record.Voice_Record()
# sys.path.append("database")
import setting
app = Flask(__name__)
socketio = SocketIO(app)
from Voice_handle import VoiceHandle
response = ""
response_tool = ""
camera_st = False
user_input_st = False
user_input_interrupt_signal = False
user_input_message = ""
SavedHistoryConversation = []  # Conversation to save when create new session
def run_graph(inputs):
    for s in graph.stream(inputs):
        if "__end__" not in s:
            print(s)
            print('------------------------')
        else:
            print(s)
            try:
                answer = AIMessage(s.get('__end__')['messages'][-1].content)
                print(answer)
                attitude = s.get('__end__')['inspector']
                print("the inspector check that the response is ",attitude)
                res = handle_event_response(attitude,answer)
                return res
            except:
                pass

def get_Chat_response(text):
    query = HumanMessage(text)
    OpenAIHistoryConversation.append(query)
    inputs = {
        "messages": OpenAIHistoryConversation
    }
    
    answer = run_graph(inputs)
    OpenAIHistoryConversation.append(answer)
    
    return answer.content
voicehandle = VoiceHandle(wake_words=['porcupine', 'jarvis'],
                          get_chat_response_func=get_Chat_response)
voicehandle.run()

def handle_event_response(attitude,answer):
    global OpenAIHistoryConversation,redirect_state
    print("check history: ",OpenAIHistoryConversation)
    if (attitude == "bad"):
        print(Fore.RED +"in the bad response")
        print(Style.RESET_ALL)
        redirect_state = "Book_researcher"
        Helper_Utilities.write_state(redirect_state)
        inputs = {
        "messages": OpenAIHistoryConversation
    }
        res  = run_graph(inputs)
        return res
    else:
        redirect_state = "supervisor"
        Helper_Utilities.write_state(redirect_state)
        return answer

@app.route("/")
def hello_world():
    return render_template('index.html',camera_state=camera_st)

def LoadBookCovers(book_ids):
    images = []
    for book_id in book_ids:
        images.append(SearchBookByID(book_id))
    return images

@app.route("/image", methods=["GET","POST"])
def get_image():
    global image_of_book
    if request.method == 'POST':
        msg = request.get_json()
        print("MSG : ", msg['id'])
        image_of_book = re.sub(r'[^0-9,]', '', msg['id']).split(',')
        # print(image_of_book)
        # print(type(image_of_book))

        images = LoadBookCovers(image_of_book)
        # print(type(images[0]))
        # return render_template('index.html')
        socketio.emit('book_images', {'visible': True, 'image' : images})
        return "load success"
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
        user_input_message = ""  
        print("/user input state posted ",data)
        if data and "input_st" in data:
            state = data["input_st"]
            user_input_st = state
            socketio.emit('user_input_state',{"state":state})
            if (state == True):
                while(user_input_message == ""):
                    continue
                print("checking the message is: ",user_input_message)
                result = user_input_message
                user_input_message = ""
                return result
            else:
                return "state is false"
        else:
            return "Invalid JSON data."
    else:
        return str(user_input_st)
@app.route("/user_input_state_interrupt",methods = ["POST","GET"])
def get_user_input_state_interrupt():
    global user_input_message
    if request.method == 'POST':
        print(" change request to the barcode scan")
        user_input_message = "***INTERRUPT***" 
    else:
        return user_input_message
    return "success"
@app.route("/return_form",methods = ["POST","GET"])
def return_form():
    if request.method == 'POST':
        data = request.get_json()
        print('//////////////////', data)
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
                SavedHistoryConversation.append("Lib : "+ msg )
                voicehandle.response_generated_by_app = msg
                t = time.localtime(time.time())
                voicehandle.response_generated_by_app = msg
                socketio.emit('update_html', {'data': msg,"time": str(t.tm_hour)+ " "+ str(t.tm_min) + " "+str(t.tm_sec)})
                return response 
            else:
                return  "No message received."
        else:
            return "Invalid JSON data."
    else:
        return  str(response_tool)

# Save history when create new session
@app.route("/saved_history", methods=["GET","POST"])
def saved_history():
    filename = "history.json"
    with open(filename,'r+', encoding='utf-8') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["HISTORY"].append(SavedHistoryConversation)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 10, ensure_ascii=False) 
    
    SavedHistoryConversation.clear()
    OpenAIHistoryConversation.clear()

@app.route("/get", methods=["GET","POST"])
def chat():
    global response
    # response = ""
    if request.method == 'POST':
        msg = request.form.get("msg")
        print("////////////////// message: ", msg)
        if msg:
            SavedHistoryConversation.append("User : "+ msg )
            response = get_Chat_response(msg)
            SavedHistoryConversation.append("Lib : "+ response )
            voicehandle.response_generated_by_app = response
            return response
        else:
            return "No message received."
    else:
        return response

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
@app.route('/listening_for_query', methods=['POST','GET'])
def voice_status_background_update():
    if request.method == 'POST':
        data = request.get_json()
        socketio.emit('voice_status_background', data)
    return ''
@app.route('/query_voice', methods=['POST','GET'])
def voice_query_background_update():
    if request.method == 'POST':
        data = request.get_json()
        socketio.emit('query_voice_background', data)
        print('query_voice_background ', data)
    return ''
@app.route('/update_status_from_voice_button', methods=['POST','GET'])
def update_from_voice_button():
    if request.method == 'POST':
        # print('voicehandle.listening_for_query', voicehandle.listening_for_query)
        if voicehandle.listening_for_query == False:
            voicehandle.responding_to_user = False
            voicehandle.listening_for_wake_word = False
            voicehandle.listening_for_query = True
            # print('voicehandle.responding_to_user: ', voicehandle.responding_to_user)
        else:
            voicehandle.reset_all()
    return ''
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
@app.route('/user_info', methods=['POST','GET'])
def receive_user_signup_info():
    if request.method == 'POST':
        username = request.form.get("username")
        password= request.form.get("pass")
        is_exist = SearchAllbyUsername(username)
        id = generate_barcode_base64()
        if (is_exist):
            # print("////////////////// username: ", is_exist)
            return "0"
        else:
            InsertUserInfo( username, password, id)
            send_img_to_email(id)
            return "1"
    else:
        return response
    
def generate_barcode_base64():
    existing_IDs = SearchAllAccountBarcode()
    # existing_IDs = []
    while True:
        unique_id = uuid.uuid4().int
    
    # Convert the ID to a string and ensure it fits the length for EAN13
        id = str(unique_id)[:12]
        if id not in existing_IDs:
            break
    # Generate barcode
    EAN = barcode.get_barcode_class('ean13')  # You can change the barcode type if needed
    ean = EAN(id, writer=ImageWriter())
    
    # Save barcode to a BytesIO object
    buffer = BytesIO()
    ean.write(buffer, options={'write_text': False})  # You can add options as needed
    
    # Rewind the buffer to the beginning
    buffer.seek(0)
    
    # Open the image with PIL and convert it to Base64
    image = Image.open(buffer)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return img_str

def send_img_to_email(base64_image, receiver_email = "vuvu3921@gmail.com"):
    sender_email = 'ronin792002@gmail.com'
    # receiver_email = 'vuvu3921@gmail.com'
    password = 'Lamvu2002'

    # Create the MIMEMultipart object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = 'Test Email from Python'

    # Email body
    body = 'This is a test email sent from Python script.'
    # base64_image = 'iVBORw0KGgoAAAANSUhEUgAAAAUA... (rest of the base64 string)'
    msg.attach(MIMEText(body, 'plain'))

    # Decode the base64 string
    image_data = base64.b64decode(base64_image)

    # Create a MIMEBase object
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(image_data)

    # Encode the payload using base64 encoding
    encoders.encode_base64(part)

    # Add header to the attachment
    part.add_header('Content-Disposition', 'attachment; filename="image.png"')

    # Attach the MIMEBase object to the MIMEMultipart object
    msg.attach(part)

    # Attach the body with the msg instance
    # msg.attach(MIMEText(body, 'plain'))

    try:
        # Create SMTP session
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Use Gmail's SMTP server
        server.starttls()  # Enable security

        # Login to the server
        server.login(sender_email, "ojeq xnrh rwbg sqxj")

        # Send the email
        server.send_message(msg)

        # Terminate the session
        server.quit()

        print('Email sent successfully!')

    except Exception as e:
        print(f'Failed to send email: {e}')
if __name__ == '__main__':
    host = setting.IP if len(setting.IP) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5001
    socketio.run(app, host=host, port=port)





