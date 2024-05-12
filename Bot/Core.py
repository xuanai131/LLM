import Helper_Utilities
from langchain_core.messages import HumanMessage, AIMessage
import requests



pre_x = ''
OpenAIHistoryConversation = []
graph = Helper_Utilities.CreateGraph(OpenAIHistoryConversation)

#  INVOKE THE TEAM
query = None
answer = None

while True:
    # query = input("nhap text: ")
    
    user_input = requests.get("http://192.168.2.206:5001/get")
    if user_input.status_code == 200 and  user_input.text!="" and user_input.text!=pre_x:
        print("____UserInput: ", user_input.text)
        query = HumanMessage(user_input.text)
        OpenAIHistoryConversation.append(query)
        inputs = {
            # "history" : [],
            "messages": OpenAIHistoryConversation
        }
        
        for s in graph.stream(inputs):
            if "__end__" not in s:
                print(s)
            else:
                print(s)
                try:
                    answer = AIMessage(s.get('__end__')['messages'][-1].content)
                    print(answer)
                except:
                    pass
        OpenAIHistoryConversation.append(answer)
        print("_____Bot: ", answer.content)
        print("-"*50)
        requests.post(url="http://192.168.2.206:5001/get", data=answer.content)

        pre_x = answer.content
        # break
       