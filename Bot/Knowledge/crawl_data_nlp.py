from time import sleep
from io import BytesIO
import os
import requests
import json
import fitz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
sys.path.append("../")
import API_keys
from Global_variable import *
# from captcha_solver import CaptchaSolver
# from python3_anticaptcha import ImageToTextTask
# from twocaptcha import TwoCaptcha
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
import ast
llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
system_prompt = ("""Bạn là một trợ lí thông minh chuyên phân tách thông tin cần thiết từ văn bản. Hãy phân tách đoạn văn bản được đưa vào 
                    theo các mục: Tác giả, Nhà xuất bản, Năm xuất bản, Call no. Nếu không tìm thấy kết quả cho mục nào thì hãy để mục đó là "None".
                    Hãy làm theo các ví dụ sau đây:
                    *Ví dụ:
                        -Input: 'Giáo trình giải tích: Trần Đức Long, Hoàng Quốc Toàn, Nguyễn Đình Sang T2 Phép tính vi phân hàm một biến dãy hàm chuỗi hàm/. -- Hà Nội: Đại Học Quốc Gia Hà Nội, 2001. - 200tr.; 21cm.
                                Sách có tại Phòng Mượn, Thư viện Đại học Sư phạm Kỹ thuật TP. Hồ Chí Minh.
                                Số phân loại: 515.07 T772-L848'
                        -Output: 'Tác giả': 'Trần Đức Long, Hoàng Quốc Toàn, Nguyễn Đình Sang', 'Nhà xuất bản': 'Đại Học Quốc Gia Hà Nội', 'Năm xuất bản': '2001', 'Call no': '515.07 T772-L848'
                    ***Lưu ý: kết quả cuối cùng phải ở dạng json.""")
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

chain = (
    prompt
    | llm
)

def process(description):
    anwser = chain.invoke({'messages': [description]})
    out = anwser.content
    dict = ast.literal_eval(out)
    return dict

# import undetected_chromedriver as uc





def save_download_state():
    with open(download_state_file,'r+', encoding='utf-8') as file:
        data = json.load(file)
        data['page_topic'] = DOWNLOAD_STATE
        data['ID'] = ID
        file.seek(0)
        json.dump(data, file, indent = 4, ensure_ascii=False) 
def clean_subject(subject):
    # Find the index of the first '(' and take the substring before it
    cleaned_subject = subject.split(' (')[0]
    # Strip any extra whitespace from the ends
    cleaned_subject = cleaned_subject.strip()
    return cleaned_subject
def trim_pdf_to_10_pages(file_path):
    pdf_document = fitz.open(file_path)
    number_of_pages = pdf_document.page_count
    if number_of_pages > 10:
        new_pdf_document = fitz.open()
        for page_number in range(10):
            new_pdf_document.insert_pdf(pdf_document, from_page=page_number, to_page=page_number)
        new_pdf_document.save(file_path)
        new_pdf_document.close()
    pdf_document.close()
def download_pdf_file(url, topic_name):
    """Download PDF from given URL to local directory.

    :param url: The url of the PDF file to be downloaded
    :return: True if PDF file was successfully downloaded, otherwise False.
    """

    # Request URL and get response object
    response = requests.get(url, stream=True)

    # isolate PDF filename from URL
    pdf_file_name = os.path.basename(url)
    if response.status_code == 200:
        # Save in current working directory
        filepath = f'/Knowledge/Books/PDF/{topic_name}/{pdf_file_name}'.split('?')[0]
        fullfilepath = AbsoluteBotPath+filepath
        with open(fullfilepath, 'wb') as pdf_object:
            pdf_object.write(response.content)
            print(f'{pdf_file_name} was successfully saved!')
        trim_pdf_to_10_pages(filepath)
        return filepath
    else:
        print(f'Uh oh! Could not download {pdf_file_name},')
        print(f'HTTP response status code: {response.status_code}')

json_file = AbsoluteBotPath+'/Knowledge/Books/Json/sample2.json'
def write_json(new_data, js_schema="book_infos"):
    with open(json_file,'r+', encoding='utf-8') as file:
        file_data = json.load(file)
        file_data[js_schema].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent = 4, ensure_ascii=False) 

def extract_namebooks_from_json(file_path, key='Tên sách', js_schema="book_infos"):
    # Initialize an empty list to store the authors
    book_names = set()
    topics = set()
    # Open and read the JSON file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)[js_schema]
        for d in data:
            book_names.add(d[key])
            topics.add(d['Loại sách'])
    return book_names, topics

NAME_BOOKS, TOPICS = extract_namebooks_from_json(json_file)
DOWNLOAD_STATE = {}
ID = 0
download_state_file = AbsoluteBotPath + '/Knowledge/download_state.json'
if not os.path.exists(download_state_file):
    # Create the file with an empty JSOsN object
    with open(download_state_file, 'w', encoding='utf-8') as file:
        data = {}
        data['page_topic'] = {}
        data['ID'] = 0
        json.dump(data, file)
else:
    with open(download_state_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        DOWNLOAD_STATE = data['page_topic']
        ID = data['ID']

options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


driver.get("https://thuvienso.hcmute.edu.vn/")

wait = WebDriverWait(driver, 20)
login_button = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='frmLogin']/p/button")))
login_button.click()
sleep(2)
wait = WebDriverWait(driver, 20)
input_email = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='identifierId']")))
input_email.send_keys("20134011@student.hcmute.edu.vn")
wait = WebDriverWait(driver, 20)
next_button = wait.until(EC.presence_of_element_located((By.XPATH,"//*[@id='identifierNext']/div/button/span")))
next_button.click()
sleep(2)
wait = WebDriverWait(driver, 20)
input_password= wait.until(EC.presence_of_element_located((By.XPATH,"//*[@id='password']/div[1]/div/div[1]/input")))
input_password.send_keys("xuanai1301#")
sleep(2)
wait = WebDriverWait(driver, 20)
next_button = wait.until(EC.presence_of_element_located((By.XPATH,"//*[@id='passwordNext']/div/button/span")))
next_button.click()

sleep(3)
# topics = [2, 6, 7, 10, 11, 13, 14, 15, 23, 24, 26, 30]
PAGES_PER_TOPIC = 10
for topic_index in range (1, 30):
    try:
        print(f'////////////////////////{topic_index}///////////')
        #Nhan cac topic lon
        topic_name =[]
        topic = wait.until(EC.presence_of_element_located((By.XPATH,f"/html/body/div[1]/div[2]/div/div[2]/div[1]/div[1]/ul/li[{topic_index}]/a/span[2]")))
        topic.click()
        
        get_topic_name = driver.find_elements(By.XPATH,f"/html/body/div[1]/div[2]/div/div[2]/div[1]/div[1]/ul/li[{topic_index}]/a/span[2]")
        topic_name.append(clean_subject(get_topic_name[0].text))
        print(topic_name)
        
        # TÌM CÁC SUBTOPIC NẾU CÓ
        try:
            sub_topic_id  = driver.find_elements(By.ID, "refontsubcate")
            # topic_name.append(i.text for i in sub_topic_id)
            if len(sub_topic_id)>1:
                for element in sub_topic_id:
                    topic_name.append(clean_subject(element.text))
                sub_topic_texts = [element.text for element in sub_topic_id]
                print(sub_topic_texts)
            # for i in range(0, len(sub_topic_id)):
            #     get_sub_topic_name = driver.find_elements(By.XPATH,f"/html/body/div[1]/div[2]/div/div[2]/div[1]/div[1]/ul/li[{i}]/a/span[2]")
        except:
            print("error_when_find_sub_topic")
        
        for k in range(1, len(topic_name)+1):
            try:
                if k == len(topic_name) and len(topic_name) > 1:
                    break
                topic_name_path= ""
                if(len(topic_name) > 1):
                    CURRENT_TOPIC_NAME = topic_name[k]
                    sub_topic = wait.until(EC.presence_of_element_located((By.XPATH,f"/html/body/div[1]/div[2]/div/div[2]/div[1]/div[1]/ul/li[{topic_index}]/ul/li[{k}]")))
                    sub_topic.click()
                    # /html/body/div[1]/div[2]/div/div[2]/div[1]/div[1]/ul/li[26]/ul/li[1]
                    topic_name_path = topic_name[0]+ "/" + topic_name[k]
                    pdf_path = os.path.join("Knowledge/Books/PDF", topic_name_path)
                #Tao folder cho tung topic
                # Path
                else:
                    topic_name_path=topic_name[0]
                    CURRENT_TOPIC_NAME = topic_name[0]
                    pdf_path = os.path.join("Knowledge/Books/PDF", topic_name[0])
                
                print("__________TOPIC NAME: ", CURRENT_TOPIC_NAME)
                if CURRENT_TOPIC_NAME not in DOWNLOAD_STATE.keys():
                    DOWNLOAD_STATE[CURRENT_TOPIC_NAME] = 0
                    TOPICS.add(CURRENT_TOPIC_NAME)
            
                os.makedirs(AbsoluteBotPath + '/' + pdf_path, exist_ok=True)
                sleep(1)
                for num_page in range(DOWNLOAD_STATE[CURRENT_TOPIC_NAME], DOWNLOAD_STATE[CURRENT_TOPIC_NAME]+PAGES_PER_TOPIC):
                    DOWNLOAD_STATE[CURRENT_TOPIC_NAME] += 1
                    for book_index in range(1, 12):
                        print(f'----------------------------{topic_index}-------------------------')
                        try:
                            wait = WebDriverWait(driver, 20)
                            title_button = wait.until(EC.presence_of_element_located((By.XPATH,f"/html/body/div[1]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/ul/li[{book_index}]/div[1]/p/a")))
                            title_button.click()
                            sleep(2)
                            
                            try:
                                pdf_link = driver.find_elements(By.XPATH,"/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[2]/div[3]/div/div[3]/embed")
                                if(len(pdf_link)==0):
                                    pdf_link = driver.find_elements(By.XPATH,"/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[2]/div[3]/div/div[2]/embed")
                                find_title_articles = driver.find_elements(By.XPATH,"/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[2]/h1")
                                find_keyword = driver.find_elements(By.XPATH,"/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[2]/div[2]/div[1]/p[1]")
                                find_description = driver.find_elements(By.XPATH,"/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[2]/div[1]")
                            except:
                                print("decription_eror")
                            
                            # try:
                            link = pdf_link[0].get_attribute('src')
                            title_articles = find_title_articles[0].text
                            keyword = [_.text for _ in find_keyword]
                            description = find_description[0].text
                            if title_articles in NAME_BOOKS:
                                if topic_name_path in TOPICS:
                                    print('_Book exist_')
                                    driver.back()
                                    continue
                            NAME_BOOKS.add(title_articles)
                            
                            
                            ID += 1   
                            new_data = process(description)
                            file_path = download_pdf_file(link, topic_name_path)
                            new_data["Tên sách"] = title_articles
                            new_data["Loại sách"] = topic_name_path
                            new_data["ID"] = ID
                            new_data["Keyword"] = keyword
                            new_data["Mô tả"] = description
                            new_data["Nội dung đầu sách"] = file_path
                            print(new_data)
                    
                            write_json(new_data) 
                            driver.back()
                        except:
                            print("Error")
                            
                    try:
                        wait = WebDriverWait(driver, 5)
                        next_bt = wait.until(EC.presence_of_element_located((By.XPATH,f"/html/body/div[1]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[3]/ul/li[8]")))
                        next_bt.click()
                    except:
                        print('_Out of pages')
                save_download_state()
            except:
                print('_________Error_________')
    except:
        print('_________Error_________')
with open(download_state_file, 'r') as json_file:
    data = json.load(json_file)

save_download_state()
driver.close()

