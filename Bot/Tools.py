from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.tools import PythonREPLTool
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from methods import *
import cv2
from langchain.agents import Tool
from pyzbar.pyzbar import decode
from book_search import *
import time
from datetime import datetime
import Helper_Utilities
import random
import book_search
import requests
import base64
import setting
    
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
    


##### LOAD DATABASE
embedding=OpenAIEmbeddings(chunk_size=1)
BookInfo =  DATABASE(db_path='/home/xuanai/html/Bot/rerievel-text/robot_knowledge_3', embedding=embedding, parent_path="/home/xuanai/html/Bot/rerievel-text/parents_3")  # Load book_info database
# RobotInfo =  DATABASE(db_path='/var/www/html/Bot/robot_info', embedding=embedding)    # Load robot_info database



##### WEB SEARCH TOOL
tavily_tool = TavilySearchResults(max_results=5)
python_repl_tool = PythonREPLTool() # This executes code locally, which can be unsafe



##### BOOK SEARCH TOOL
# book_retriever = BookInfo.db.as_retriever(
#     search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.3, "k": 4}
# )

def load_book(book_ids: str):
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
        
    except:
        print("cant send")
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
def scan_barcode(ten_sach: str):  # define scan function to scan barcode
    requests.post(setting.IP_ADDRESS+'/camera_status',data = {'camera_status': True})
    t = time.time()
    # image_path = '384543478_1440448783351821_8320517275639987477_n.jpg'  # Replace 'images' with the path to your directory
    # image = cv2.imread(image_path)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
    cap.set(cv2.CAP_PROP_FPS, 25)
    if not cap.isOpened():
        return "ERROR"
    while True:
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
                return data
        except:
            continue


def send_borrowstudent_to_form(student_id):
    student_info = search_all_by_studentID_in_studentinfo(student_id)
    data = {}
    data['type'] = 'student'
    data['name'] = student_info[2]
    data['ID'] = student_info[1]
    data['year'] = student_info[3]
    data['faculty'] = student_info[4]
    data['major'] = student_info[5]
    data['images'] = student_info[-1]
    requests.post(url=setting.IP_ADDRESS+"/student-book_info", json=data)
    requests.post(url=setting.IP_ADDRESS+"/borrow_book_student_info", json=data)
    print('///////////////////////////// student')
def send_borrowbook_to_form(book_name):
    book_info = search_book_by_name_in_books(book_name)
    data = {}
    data['type'] = 'borrow'
    data['images'] = book_info[-2]
    requests.post(url=setting.IP_ADDRESS+"/student-book_info", json=data)
    print('///////////////////////////// borrow book')

def borrow_book(name_book: str):
    send_mess("start", "return_form")
    result = {'Sinh viên': '', 'Sách': []}
    Student_ID = ''
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
    result['Sinh viên'] = str(list(search_studentinfo_by_id(Student_ID))[:-1])
    
    time.sleep(1)
    while True:
        send_mess("Xin hãy đưa sách vào khe bên dưới.")
        Book_ID = scan_barcode('')
        if Book_ID == "OVERTIME":
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
        elif Book_ID == "ERROR":
            send_mess("stop", "return_form")
            return "Camera không có sẵn"
        else:
            book_item = search_book_by_id_in_bookitem(Book_ID)
            if book_item[2]=='false':
                send_mess('Xin lỗi nhưng cuốn sách này đã được ai đó mượn rồi, bạn có muốn mướn cuốn nào khác không?')
                user_input = user_input_request(True)
                if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                    continue
                else:
                    break
            book_name = search_name_by_bookID_in_bookitem(Book_ID)
            send_borrowbook_to_form(book_name)
            result['Sách'].append(str(search_book_by_id_in_bookitem(Book_ID)))
            send_mess("Bạn có muốn mượn cuốn sách nào nữa không?")
            user_input = user_input_request(True)
            if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                continue
            else:
                break
    if len(result['Sách']) > 0:
        # Xử lí mượn sách tại đây
        user_input_request(False)
        send_mess("stop", "return_form")
        return str(result)
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
    requests.post(url=setting.IP_ADDRESS+"/"+topic, json={"message":str})
def user_input_request(state):
    res = requests.post(url=setting.IP_ADDRESS+"/user_input_state", json={"input_st":state})
    return res.text

def show_return_form(book_ids):
    imageID= {
        "id": book_ids
    }
    
    headers = {'Content-Type': 'application/json'}
    requests.post(url=setting.IP_ADDRESS+"/image", json=imageID, headers=headers)
##### RETURN BOOK TOOL
def send_returnbook_to_form(Book_ID, borrow_date, studentinfo):
    book_name = search_name_by_bookID_in_bookitem(Book_ID)
    book_info = search_book_by_name_in_books(book_name)
    data = {}
    data['type'] = 'return'
    data['images'] = book_info[-2]
    data['borrow_date'] = borrow_date
    data['student_name'] = studentinfo[2]
    data['student_ID'] = studentinfo[1]
    requests.post(url=setting.IP_ADDRESS+"/student-book_info", json=data)
    print('SENT.......................')
    
def return_book(name_book: str):
    result = {'Sách': [], 'Sinh viên': []}
    send_mess("start", "return_form")
    send_mess("Xin hãy đưa sách vào khe bên dưới.")
   
    while True:
        Book_ID = scan_barcode('') # Quét mã vạch sách
        if Book_ID == "OVERTIME":
            send_mess("Xin lỗi, mình chưa quét được mã vạch, bạn có muốn quét lại không?")
            user_input = user_input_request(True)
            # print("user input ",user_input)
            
            if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                continue
            else:
                user_input_request(False)
                break
        elif Book_ID == "ERROR":
            send_mess("stop", "return_form")
            return "Camera không có sẵn"
        else:
            bill_info = search_all_by_bookID_in_Bill(Book_ID)
            if bill_info is None:
                send_mess("Xin lỗi, có vẻ như cuốn sách này chưa được mượn ở thư viện.")
                send_mess("Bạn có muốn trả cuốn sách nào nữa không?")
                user_input = user_input_request(True)
                if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                    continue
                else:
                    user_input_request(False)
                    break
            if bill_info[4] is not None:
                send_mess("Xin lỗi, có vẻ như cuốn sách này đã được trả rồi.")
                send_mess("Bạn có muốn trả cuốn sách nào nữa không?")
                user_input = user_input_request(True)
                if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                    continue
                else:
                    user_input_request(False)
                    break
                
            Student_ID = bill_info[1]
            result['Sách'].append(search_book_by_id_in_bookitem(Book_ID))
            studentinfo = search_studentinfo_by_id(Student_ID)
            result['Sinh viên'].append(list(studentinfo)[:-1])
            # Send info return to the website
            send_returnbook_to_form(Book_ID, bill_info[3], studentinfo)
            send_mess("Bạn có muốn trả cuốn sách nào nữa không?")
            user_input = user_input_request(True)
            if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                continue
            else:
                break
    if len(result['Sách']) > 0:
        send_mess(f"Có phải bạn muốn trả những cuốn sách {[_[1] for _ in result['Sách']]} không. Xin hãy xác nhận lại để mình hoàn thành việc trả sách")
        user_input = user_input_request(True)
        if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
            books_return_id = [_[0] for _ in result['Sách']]
            # show_return_form(books_return_id)
            for s in result['Sách']:
                send_mess("stop", "return_form")
                update_bill_return(s[0], datetime.now())
            user_input_request(False)
            return "Quá trình trả sách Hoàn tất"
        else:
            user_input_request(False)
            
    send_mess("stop", "return_form")
    return "Quá trình trả sách không được thực hiện, cảm ơn bạn đã sử dụng dịch vụ."
    
    
    
    

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
        book_search.update_bill_return(ID, return_day)
        book_search.update_isavailable_state('true', ID)
        update_bill_return(ID, return_day)
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
