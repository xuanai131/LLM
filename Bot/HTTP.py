import requests
import time
IP_address = '192.168.2.206' # Server address
HTTP_Port = "5000"


# Post message to server in specific topic
def Post(topic, message):
    url = f'http://{IP_address}:{HTTP_Port}/{topic}'
    myobj = message.encode('utf-8')

    try:
        response = requests.post(url, data=myobj)

        # Check if the request was successful (status code 2xx)
        if response.status_code // 100 == 2:
            pass
        else:
            print(f"POST request failed with status code {response.status_code}: {response.text}")

    except requests.RequestException as e:
        print(f"POST request failed: {e}")
        
        
# Get response from server base on specific topic
def GetServerResponse(topic):
    url = f'http://{IP_address}:{HTTP_Port}/{topic}'
    try:
        response = requests.get(url)
        # Check if the request was successful (status code 2xx)
        if response.status_code // 100 == 2:
            return response.text
        else:
            print(f"GET request failed with status code {response.status_code}: {response.text}")
            return 

    except requests.RequestException as e:
        print(f"GET request failed: {e}")
