import requests
pre_x = ""


while True:
    # query = input("nhap text: ")
    
    x = requests.get("http://192.168.2.206:5001/get")
    # x = x[0]
    if x.status_code == 200 and x.text!="" and x!=pre_x:
        
        # respnse ={
        #     'mess': 'Your message here'
        # }
        respnse = "received :" + "some text " +x.text
        print(respnse)
        res = requests.post(url="http://192.168.2.206:5001/get", data=respnse)
        if res.status_code == 204:
            print("Request succeeded with status 204 (No Content)")
        elif res.status_code == 200:
            print("Request succeeded with status 200 (OK)")
        else:
            print(f"Request failed with status {res.status_code}")
        pre_x = x
        # break