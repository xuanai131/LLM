from time import sleep
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
from Global_variable import *
# from captcha_solver import CaptchaSolver
# from python3_anticaptcha import ImageToTextTask
# from twocaptcha import TwoCaptcha


# import undetected_chromedriver as uc


import requests
from io import BytesIO
# from PIL import Image

import os
import requests
import json

# def handle_capcha(index, driver1):
#     #download capcha
#     image_element= driver1.find_elements(By.XPATH, "/html/body/div[1]/div[2]/div/div[2]/div[2]/div[1]/div/div/div/div[2]/form/div/ul/li[1]/span[1]/img")
#     image_url = image_element[0].get_attribute("src")
    
#     # Skip if the image URL is empty
#     if not image_url:
#         return
    
#     # Download the image content
#     response = requests.get(image_url)
    
#     # Open the image using PIL (Python Imaging Library)
#     image = Image.open(BytesIO(response.content))
    
#     # Save the image to the folder
#     image.save(f"images/image_{index}.png")
    
    
#     #handle capcha
#     captcha_image = f"images/image_{index}.png"
#     ANTICAPTCHA_KEY = 'masked'  
#     result = ImageToTextTask.ImageToTextTask(
#         anticaptcha_key=ANTICAPTCHA_KEY).captcha_handler(captcha_file=captcha_image)
    
#     # captcha_text = result['solution']['text']
    
#     return result


#download pdf

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
        return filepath
    else:
        print(f'Uh oh! Could not download {pdf_file_name},')
        print(f'HTTP response status code: {response.status_code}')
    
def write_json(new_data, filename=AbsoluteBotPath+'/Knowledge/Books/Json/sample.json', js_schema="book_infos"):
    with open(filename,'r+', encoding='utf-8') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data[js_schema].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 10, ensure_ascii=False) 

options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


driver.get("https://thuvienso.hcmute.edu.vn/")

wait = WebDriverWait(driver, 20)
login_button = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='frmLogin']/p/button")))
login_button.click()
sleep(3)
wait = WebDriverWait(driver, 20)
input_email = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='identifierId']")))
input_email.send_keys("20134028@student.hcmute.edu.vn")
wait = WebDriverWait(driver, 20)
next_button = wait.until(EC.presence_of_element_located((By.XPATH,"//*[@id='identifierNext']/div/button/span")))
next_button.click()
sleep(3)
wait = WebDriverWait(driver, 20)
input_password= wait.until(EC.presence_of_element_located((By.XPATH,"//*[@id='password']/div[1]/div/div[1]/input")))
input_password.send_keys("Lamvu2002")
sleep(3)
wait = WebDriverWait(driver, 20)
next_button = wait.until(EC.presence_of_element_located((By.XPATH,"//*[@id='passwordNext']/div/button/span")))
next_button.click()

sleep(10)
count = 34
topics = [2, 6, 7, 10, 11, 13, 14, 15, 23, 24, 26, 30]
for i in range (7, 30):
    wait = WebDriverWait(driver, 20)
    
    #Nhan cac topic lon
    topic = wait.until(EC.presence_of_element_located((By.XPATH,f"/html/body/div[1]/div[2]/div/div[2]/div[1]/div[1]/ul/li[{i}]")))
    topic.click()
    
    get_topic_name = driver.find_elements(By.XPATH,f"/html/body/div[1]/div[2]/div/div[2]/div[1]/div[1]/ul/li[{i}]/a/span[2]")
    topic_name = get_topic_name[0].text
    print("TOPIC NAME: ", topic_name)
    
    #Tao folder cho tung topic
    
    # Path 
    path = os.path.join("Books/PDF", topic_name) 
   
    os.mkdir(path) 
    if i in topics:
        number_articles = 20
    else:
        number_articles = 5
    index_of_articles = 1
    sleep(1)
    while(index_of_articles <= number_articles):
        try:
            wait = WebDriverWait(driver, 20)
            title_button = wait.until(EC.presence_of_element_located((By.XPATH,f"/html/body/div[1]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/ul/li[{index_of_articles}]/div[1]/p/a")))
            title_button.click()
            sleep(1)
            
            #pdf link
            pdf_link = driver.find_elements(By.XPATH,"/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[2]/div[3]/div/div[3]/embed")
            find_title_articles = driver.find_elements(By.XPATH,"/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[2]/h1")
            find_keyword = driver.find_elements(By.XPATH,"/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[2]/div[2]/div[1]/p[1]")
            find_introduction = driver.find_elements(By.XPATH,"/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[2]/div[1]")
            find_description = driver.find_elements(By.XPATH,"/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[2]/div[1]")
        
            link = pdf_link[0].get_attribute('src')
            title_articles = find_title_articles[0].text
            keyword = [i.text for i in find_keyword]
            introduction = find_introduction[0].text
            description = find_description[0].text
            print("PDF LINK: ", link)
            print("title_articles: ", title_articles)
            print("description: ", description)
            print("keyword: ", keyword)
            
            
            file_path = download_pdf_file(link, topic_name)
            count += 1
            if count == 10:
                break
            
            new_data = {}
            new_data["Tên sách"] = title_articles
            new_data["Loại sách"] = topic_name
            new_data["ID"] = count
            new_data["Keyword"] = keyword
            new_data["Mô tả"] = description
            new_data["Vị trí"] = "Kệ số " + str(count)
            new_data["Nội dung đầu sách"] = file_path
            # new_data = {"Topic": topic_name,
            #             "Tiêu đề": title_articles,
            #             "Tác giả": "none",
            #             "NXB": "None",
            #             "Từ khóa": keyword,
            #             "Giới thiệu": introduction,
            #             "Lời nói đầu": "None",
            #             "Mục lục": "None"
            #             }
            # print(new_data)
            write_json(new_data) 
        except:
            print("Error")
        
        index_of_articles += 1  
        driver.back()
        
    sleep(1)
# /html/body/div[1]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/ul/li[1]/div[1]/p/a
# /html/body/div[1]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/ul/li[2]/div[1]/p/a
# /html/body/div[1]/div[2]/div/div[2]/div[1]/div[1]/ul/li[1]
# /html/body/div[1]/div[2]/div/div[2]/div[1]/div[1]/ul/li[2]
# /html/body/div[1]/div[2]/div/div[2]/div[1]/div[1]/ul/li[24]
# /html/body/div[1]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/ul/li[1]/div[1]/div[2]/p[2]/button
# /html/body/div[1]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/ul/li[2]/div[1]/div[2]/p[2]/button

driver.close()

