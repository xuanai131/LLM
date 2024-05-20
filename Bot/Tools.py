from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.tools import PythonREPLTool
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from methods import *
from Global_variable import *
import cv2
from langchain.agents import Tool
from pyzbar.pyzbar import decode
from Database_handle import *
import time
from datetime import datetime
import Helper_Utilities
import requests
import base64
import setting
import threading
import queue
load_tool_execute = False
lock = threading.Lock()
result_store = {"barcode_return": "","user_input_return" : "" }
event = threading.Event()
def turn_on_camera():
    response = requests.get(setting.IP_ADDRESS+'/camera_status')
    if response.status_code == 200:
        print("Camera turned on successfully")
    else:
        print("Failed to turn on camera")

##### CREATE USER_INPUT FUNCTION
def UserInput():
    print("_________You: ", end ='')
    user_input = input()
    return user_input
    


##### LOAD VECTOR DATABASE
embedding=OpenAIEmbeddings(chunk_size=1)
BookInfoRetriever = RETRIEVER_CONFIG()
BookInfo =  DATABASE(db_path=AbsoluteBotPath+'/vector_database/book_infos_3', 
                     embedding=embedding, 
                     parent_path=AbsoluteBotPath+"/vector_database/book_parents_3", 
                     retriever_config=BookInfoRetriever)

SelfKnowledgeRetriever = RETRIEVER_CONFIG()
SelfKnowledgeRetriever.child_splitter = RecursiveCharacterTextSplitter(
                separators=["\n","\n\n" "\\n", "\\n\\n", '",', '. ', "-", "--"],
                chunk_size=120,
                chunk_overlap=20,
                length_function=len,
                is_separator_regex=False,
            )
SelfKnowledgeRetriever.parent_splitter = RecursiveCharacterTextSplitter(chunk_size=500, 
                                                 chunk_overlap= 20, 
                                                 separators=[".", "-", "--"])
SelfKnowledgeRetriever.retriever_type = "NoCustom"
SelfKnowledge =  DATABASE(db_path=AbsoluteBotPath+'/vector_database/self_knowledge', 
                          embedding=embedding, 
                          parent_path=AbsoluteBotPath+"/vector_database/self_knowledge_parents", 
                          retriever_config=SelfKnowledgeRetriever)



##### SELF KNOWLEDGE SEARCH TOOL
self_knowledge_tool=[
    create_retriever_tool(
        SelfKnowledge.retriever,
        "self_knowledge",
        "trả lời các câu hỏi liên quan đến công việc của bạn, hoặc liên quan đến thư viện trường.",
    )
]


##### WEB SEARCH TOOL
tavily_tool = TavilySearchResults(max_results=5)
python_repl_tool = PythonREPLTool() # This executes code locally, which can be unsafe



##### BOOK SEARCH TOOL
# book_retriever = BookInfo.db.as_retriever(
#     search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.3, "k": 4}
# )

def load_book(book_ids: str):
    global load_tool_execute
    load_tool_execute = True
    # turn_on_camera()
    imageID= {
        "id": book_ids
    }

    print("=============================")
    print("ID: ", imageID)
    print("=============================")
    
    headers = {'Content-Type': 'application/json'}
    try:
        res = requests.post(url=setting.IP_ADDRESS+"/image", json=imageID, headers=headers)
        if res.status_code == 200:
                print("Request succeeded with status 200 (OK)")
                return " Load the book sucessfully "
    except:
        print("cant send")
        return " Load the book sucessfully "
        pass

   
book_search_tool=[
    create_retriever_tool(
        BookInfo.retriever,
        "book_researcher",
        "tìm kiếm và trả lời các thông tin về sách trong database của thư viện cho người dùng",
    ),
    Tool(
        name="load_book",
        func=load_book,
        description="In ra id của tất cả cuốn sách tìm được",
    )
]

# BookSearchTool =  create_retriever_tool(
#         book_retriever,
#         "book_researcher",
#         "tìm kiếm và trả lời các thông tin về sách trong database của thư viện cho người dùng",
#     )


# book_search_tool = create_retriever_tool(
#     book_retriever,
#     "book_researcher",
#     "tìm kiếm và trả lời các thông tin về sách trong database của thư viện cho người dùng",
# )




##### BORROW BOOK TOOL
def scan_barcode(ten_sach: str):
    global result_store  # define scan function to scan barcode
    requests.post(setting.IP_ADDRESS+'/camera_status',data = {'camera_status': True})
    t = time.time()
    # image_path = '384543478_1440448783351821_8320517275639987477_n.jpg'  # Replace 'images' with the path to your directory
    # image = cv2.imread(image_path)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
    cap.set(cv2.CAP_PROP_FPS, 25)
    if not cap.isOpened():
        result_store['barcode_return'] = "ERROR"
        return "ERROR"
    while not event.is_set():
        # Capture frame-by-frame
        ret, image = cap.read()
        # cv2.imshow('image', image)
        # cv2.imwrite('capture.jpg', image)
        # Encode frame as base64
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        # Send base64 image to server
        url = setting.IP_ADDRESS+'/camera'
        payload = {'image_base64': image_base64}
        try:
            response = requests.post(url, data=payload)
            print("Image sent to server")
        except requests.RequestException as e:
            print("Error sending image to server:", e)
        
        if cv2.waitKey(1) == ord('q'):
            cap.release()
            # cv2.destroyAllWindows()
        
        if (time.time() - t) > 20:
            requests.post(setting.IP_ADDRESS+'/camera_status',data = {'camera_status': False})
            requests.post(setting.IP_ADDRESS+"/user_input_state_interrupt",data = {"user_input_state":False})
            result_store['barcode_return'] = "OVERTIME"
            return "OVERTIME"
        try:
            # Convert the image to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Detect barcodes in the image
            decoded_objects = decode(gray)


            # Process each detected barcode and cut it into a new image
            for i, obj in enumerate(decoded_objects):
                data = obj.data.decode('utf-8')  # Extract the barcode data
                cap.release()
                # cv2.destroyAllWindows()
                # cv2.destroyWindow('image')
                requests.post(setting.IP_ADDRESS+'/camera_status',data = {'camera_status': False})
                result_store['barcode_return'] = data
                requests.post(setting.IP_ADDRESS+"/user_input_state_interrupt",data = {"user_input_state":False})
                return data
        except:
            continue
    result_store['barcode_return'] = "INTERRUPT"
    return "INTERRUPT"


def send_borrowstudent_to_form(student_id):
    student_info = SearchStudentInfo(student_id)
    data = {}
    data['type'] = 'student'
    data['name'] = student_info['student_name']
    data['ID'] = student_info['student_ID']
    data['year'] = student_info['school_year']
    data['faculty'] = student_info['faculty']
    data['major'] = student_info['major']
    data['images'] = student_info['student_image']
    requests.post(url=setting.IP_ADDRESS+"/student-book_info", json=data)
    requests.post(url=setting.IP_ADDRESS+"/borrow_book_student_info", json=data)
    print('///////////////////////////// student')
def send_borrowbook_to_form(book_ID):
    book_info = SearchBookByID(book_ID)
    data = {}
    data['type'] = 'borrow'
    data['images'] = book_info['cover_image']
    requests.post(url=setting.IP_ADDRESS+"/student-book_info", json=data)
    print('///////////////////////////// borrow book')

def borrow_book(name_book: str):
    send_mess("start", "return_form")
    result = {'Sinh viên': '', 'Sách': []}
    Student_ID = ''
    barcode_list = []
    while True:
        send_mess("Xin hãy đưa thẻ sinh viên vào khe bên dưới.")
        Student_ID = scan_barcode('')
        if Student_ID == "OVERTIME":
            send_mess("Xin lỗi, mình chưa quét được mã vạch, bạn có muốn quét lại không?")
            user_input = user_input_request(True)
            # user_input = UserInput()
            # print("user input ",user_input)
            
            if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                continue
            else:
                user_input_request(False)
                send_mess("stop", "return_form")
                return "Quá trình mượn sách không được thực hiện, cảm ơn bạn đã sử dụng dịch vụ."
        elif Student_ID == "ERROR":
            send_mess("stop", "return_form")
            return "Camera không có sẵn"
        else:
            break
    send_borrowstudent_to_form(Student_ID)
    result['Sinh viên'] = SearchStudentInfo(Student_ID)
    
    time.sleep(1)
    while True:
        send_mess("Xin hãy đưa sách vào khe bên dưới.")
        barcode = scan_barcode('')
        if barcode == "OVERTIME":
            send_mess("Xin lỗi, mình chưa quét được mã vạch, bạn có muốn quét lại không?")
            user_input = user_input_request(True)
            # user_input = UserInput()
            print("user input ",user_input)
            
            if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                continue
            else:
                user_input_request(False)
                # send_mess("stop", "return_form")
                break
        elif barcode == "ERROR":
            send_mess("stop", "return_form")
            return "Camera không có sẵn"
        else:
            state = SearchIsavailableState(barcode)
            if state==False:
                send_mess('Xin lỗi nhưng cuốn sách này đã được ai đó mượn rồi, bạn có muốn mướn cuốn nào khác không?')
                user_input = user_input_request(True)
                if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                    continue
                else:
                    break
            barcode_list.append(barcode)
            book_ID = SearchBookIDByBarcode(barcode)
            send_borrowbook_to_form(book_ID)
            temp_book_info = SearchBookByID(book_ID)
            temp_book_info.pop('cover_image')
            result['Sách'].append(temp_book_info)
            send_mess("Bạn có muốn mượn cuốn sách nào nữa không?")
            user_input = user_input_request(True)
            if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                continue
            else:
                break
    if len(result['Sách']) > 0:
        print('////////............/////', result['Sách'])
        # Xử lí mượn sách tại đây
        for bc in barcode_list:
            CreateBill(bc, Student_ID, datetime.now())
            UpdateIsavailableState(False, bc)
        user_input_request(False)
        # send_mess("stop", "return_form")
        return str(result['Sách'])
    user_input_request(False)
    send_mess("stop", "return_form")
    return "Quá trình mượn sách không được thực hiện, cảm ơn bạn đã sử dụng dịch vụ."


borrow_book_tool = [
    Tool(
        name="Borrow_book",
        func=borrow_book,
        description="Hữu ích trong việc giúp người dùng mượn sách",
    )
]


def confirm_borrow_completely(n: str):
    # print("Đã xử lí xong mượn sách !!!")
    response = input()
    return response
    
confirm_borrow_conpletely_tool = [
    Tool(
        name="Confirm_borrow",
        func=confirm_borrow_completely,
        description="Hữu ích trong việc phản hồi lại xác nhận mượn sách của người dùng",
    )
]

def send_mess(str, topic="tool_action"):
    print(str)
    user_input_request(False)
    requests.post(url=setting.IP_ADDRESS+"/"+topic, json={"message":str})
def user_input_request(state):
    global result_store
    res = requests.post(url=setting.IP_ADDRESS+"/user_input_state", json={"input_st":state})
    if state:
        result_store["user_input_return"] = res.text
    return res.text

def show_return_form(book_ids):
    imageID= {
        "id": book_ids
    }
    
    headers = {'Content-Type': 'application/json'}
    requests.post(url=setting.IP_ADDRESS+"/image", json=imageID, headers=headers)
##### RETURN BOOK TOOL
def send_returnbook_to_form(barcode, borrow_date, studentinfo):
    book_ID = SearchBookIDByBarcode(barcode)
    book_info = SearchBookByID(book_ID)
    data = {}
    data['type'] = 'return'
    data['images'] = book_info['cover_image']
    data['borrow_date'] = borrow_date
    data['student_name'] = studentinfo['student_name']
    data['student_ID'] = studentinfo['student_ID']
    requests.post(url=setting.IP_ADDRESS+"/student-book_info", json=data)
    print('SENT.......................')
# user post the input while camera is running
def user_input_request_thread(state):
    res = user_input_request(state)
    if (res!="***INTERRUPT***"):
        check_interrupt = Helper_Utilities.book_return_interrupt_chain.invoke({'messages': [res]})['messages'] 
        print("interrupt detect :",check_interrupt)
        if(check_interrupt == "yes"):
            event.set()

def do_return_book(name_book:str):
    global result_store
    result = {'Sách': [], 'Sinh viên': []}
    send_mess("start", "return_form")
    send_mess("Xin hãy đưa sách vào khe bên dưới.")
    barcode_list = []
    while True:
        # Book_ID = scan_barcode('') # Quét mã vạch sách
        event.clear()
        result_store.clear()
        thread1 = threading.Thread(target=user_input_request_thread, args=(True,))
        thread2 = threading.Thread(target=scan_barcode, args=('value',))
        thread1.start()
        thread2.start()

        # Waiting for both threads to finish
        thread1.join()
        thread2.join()
        # Book_ID = scan_barcode('')
        Book_ID = result_store["barcode_return"]
        if Book_ID == "OVERTIME":
            send_mess("Xin lỗi, mình chưa quét được mã vạch, bạn có muốn quét lại không?")
            user_input = user_input_request(True)
            # print("user input ",user_input)
            
            if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                continue
            else:
                user_input_request(False)
                break
        elif result_store["barcode_return"] == "ERROR":
            send_mess("stop", "return_form")
            return "Camera không có sẵn"
        elif result_store["barcode_return"] == "INTERRUPT":
            send_mess("stop", "return_form")
            return "Quá trình trả sách đã bị dừng"
        else:
            # bill_info = SearchBillByBarcode(barcode)
            bill_info = {"student_ID":"20134013","return_date":None,'borrow_date':"08-01-2018"}
            if bill_info is None:
                send_mess("Xin lỗi, có vẻ như cuốn sách này chưa được mượn ở thư viện.")
                send_mess("Bạn có muốn trả cuốn sách nào nữa không?")
                user_input = user_input_request(True)
                if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                    user_input_request(False)
                    continue
                else:
                    user_input_request(False)
                    break
            if bill_info['return_date'] is not None:
                send_mess("Xin lỗi, có vẻ như cuốn sách này đã được trả rồi.")
                send_mess("Bạn có muốn trả cuốn sách nào nữa không?")
                user_input = user_input_request(True)
                if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                    continue
                else:
                    user_input_request(False)
                    break
                
            Student_ID = bill_info['student_ID']
            barcode_list.append(Book_ID)
            book_IDs = SearchBookIDByBarcode(Book_ID)
            temp_book_info = SearchBookByID(book_IDs)
            temp_book_info.pop('cover_image')
            result['Sách'].append(temp_book_info)
            student_info = SearchStudentInfo(Student_ID)
            result['Sinh viên'].append(student_info)
            # Send info return to the website
            send_returnbook_to_form(Book_ID, bill_info['borrow_date'], student_info)
            send_mess("Bạn có muốn trả cuốn sách nào nữa không?")
            user_input = user_input_request(True)
            if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                continue
            else:
                break
    if len(barcode_list) > 0:
        send_mess(f"Có phải bạn muốn trả những cuốn sách {[_['name_of_book'] for _ in result['Sách']]} không. Xin hãy xác nhận lại để mình hoàn thành việc trả sách")
        user_input = user_input_request(True)
        if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
            # books_return_id = [_[ID] for _ in result['Sách']]
            # show_return_form(books_return_id)
            for bc in barcode_list:
                UpdateBillReturn(bc, datetime.now())
                UpdateIsavailableState(True, bc)
            # send_mess("stop", "return_form")RETURN_BOOK_PROMPT
            user_input_request(False)
            return "Quá trình trả sách Hoàn tất"
        else:
            user_input_request(False)
            return "Quá trình trả sách không được thực hiện, cảm ơn bạn đã sử dụng dịch vụ."
    send_mess("stop", "return_form")
    return "Quá trình trả sách không được thực hiện, cảm ơn bạn đã sử dụng dịch vụ."
def return_book(name_book: str):

    res = do_return_book(name_book)
    print ("do book return :",res)
    return res
    
    
    
    

return_book_tool = [
    Tool(
        name="Return_book",
        func=return_book,
        description="Hữu ích trong việc giúp người dùng trả sách",
    )
]

def process_return(book_IDs: str):
    list_ID = book_IDs.split(',')
    # print(list_ID)
    for ID in list_ID:
        return_day = datetime.datetime.now()
        UpdateBillReturn(ID, return_day)
        UpdateIsavailableState(True, ID)
    return "Return successfully"

# return_book_tool = [
#     Tool(
#         name="Scan_barcode",
#         func=scan_barcode,
#         description="Hữu ích trong việc quét mã vạch",
#     ),
#     Tool(
#         name="Process_return",
#         func=process_return,
#         description="Thực hiện quá trình trả sách",
#     )
# ]
