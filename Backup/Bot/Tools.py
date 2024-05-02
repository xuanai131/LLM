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

def turn_on_camera():
    response = requests.get('http://192.168.2.206:5001/camera_status')
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
embedding=OpenAIEmbeddings()
BookInfo =  DATABASE(db_path='book_info', embedding=embedding)  # Load book_info database
RobotInfo =  DATABASE(db_path='robot_info', embedding=embedding)    # Load robot_info database


##### WEB SEARCH TOOL
tavily_tool = TavilySearchResults(max_results=5)
python_repl_tool = PythonREPLTool() # This executes code locally, which can be unsafe



##### BOOK SEARCH TOOL
book_retriever = BookInfo.db.as_retriever(
    search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.3, "k": 4}
)

def load_book(book_ids: str):
    # turn_on_camera()
    imageID= {
            "id": [book_ids]
    }
    
    headers = {'Content-Type': 'application/json'}
    try:
        res = requests.post(url="http://192.168.2.206:5001/image", json=imageID, headers=headers)
        if res.status_code == 200:
                print("Request succeeded with status 200 (OK)")

        print("ID: ")
    # images = []
    # for book_id in book_ids:
    
        print(imageID)
    #     images.append("data:image/jpeg;base64," + str(book_search.search_book_image_by_id(book_id)[0]))
    # return book_ids
    except:
        pass

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
    requests.post('http://192.168.2.206:5001/camera_status',data = {'camera_status': True})
    t = time.time()
    # image_path = '384543478_1440448783351821_8320517275639987477_n.jpg'  # Replace 'images' with the path to your directory
    # image = cv2.imread(image_path)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('captured3')
        return "Không có camera để quét barcode"
    while True:
        # Capture frame-by-frame
        ret, image = cap.read()
        # cv2.imshow('image', image)
        # cv2.imwrite('capture.jpg', image)
        # Encode frame as base64
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        # Send base64 image to server
        url = 'http://192.168.2.206:5001/camera'
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
            requests.post('http://192.168.2.206:5001/camera_status',data = {'camera_status': False})
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
                requests.post('http://192.168.2.206:5001/camera_status',data = {'camera_status': False})
                return data
        except:
            continue
        
def borrow_book(name_book: str):
    result = {}
    print("Xin hãy đưa sách vào khe bên dưới.")
    Book_ID = scan_barcode('')
    result['Sách'] = str(search_book_by_id_in_bookitem(Book_ID))
    time.sleep(1)
    
    print("Xin hãy đưa thẻ sinh viên vào khe bên dưới.")
    Student_ID = scan_barcode('')
    try :
        result['Sinh viên'] = str(list(search_studentinfo_by_id(Student_ID))[:-1])
    except:
        result['Sinh viên'] = "['Không có thông tin']"
    
    return str(result)

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



##### RETURN BOOK TOOL
def return_book(name_book: str):
    result = {'Sách': [], 'Sinh viên': []}
    print("Xin hãy đưa sách vào khe bên dưới.")
    while True:
        Book_ID = scan_barcode('')
        if Book_ID == "OVERTIME":
            print("Xin lỗi, mình chưa quét được mã vạch, bạn có muốn quét lại không?")
            user_input = UserInput()
            if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                continue
            else:
                return "Quá trình trả sách không được thực hiện, cảm ơn bạn đã sử dụng dịch vụ."
        else:
            Student_ID = search_studentID_by_boookID_in_Bill(Book_ID)
            if Student_ID is None:
                print("Xin lỗi, có vẻ như cuốn sách này chưa được mượn ở thư viện hoặc bạn đã trả nó trước đó rồi.")
                print("Bạn có muốn trả cuốn sách nào nữa không?")
                user_input = UserInput()
                if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                    continue
                else:
                    return "Quá trình trả sách không được thực hiện, cảm ơn bạn đã sử dụng dịch vụ."
                
            result['Sách'].append(search_book_by_id_in_bookitem(Book_ID))
            result['Sinh viên'].append(list(search_studentinfo_by_id(Student_ID))[:-1])
            
            print("Bạn có muốn trả cuốn sách nào nữa không?")
            user_input = UserInput()
            if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                continue
            else:
                print(f"Có phải bạn muốn trả những cuốn sách {[_[0][1] for _ in result['Sách']]} không. Xin hãy xác nhận lại để mình hoàn thành việc trả sách")
                user_input = UserInput()
                if Helper_Utilities.classify_chain.invoke({'messages': [user_input]})['messages'] == 'affirm':
                    for s in result['Sách']:
                        update_bill_return(s[0][0], datetime.now())
                    return "Quá trình trả sách đã hoàn tất, cảm ơn bạn dã sử dụng dịch vụ."
                else:
                    return "Quá trình trả sách không được thực hiện, cảm ơn bạn đã sử dụng dịch vụ."
    
    
    
    

return_book_tool = [
    Tool(
        name="Return_book",
        func=return_book,
        description="Hữu ích trong việc giúp người dùng trả sách",
    )
]

   
book_search_tool=[
    create_retriever_tool(
        book_retriever,
        "book_researcher",
        "tìm kiếm và trả lời các thông tin về sách trong database của thư viện cho người dùng",
    ),
    Tool(
        name="load_book",
        func=load_book,
        description="In ra id của từng cuốn sách tìm được",
    )
]
