import Helper_Utilities
from langchain_core.messages import HumanMessage, AIMessage
import HTTP




OpenAIHistoryConversation = []
graph = Helper_Utilities.CreateGraph(OpenAIHistoryConversation)

#  INVOKE THE TEAM
query = None
answer = None
while True:
    print("_________You: ", end ='')
    user_input = input()
    # while True:
    #     user_input = HTTP.GetServerResponse('get')
    #     # print('user_input:    ', type(user_input))
    #     if user_input != None:
    #         break
            
    print(user_input)
    if user_input=='quit' or user_input=='exit':
        break
    
    print('............. Generating .............', end='\r')
    print("________Bot: ")
    
    query = HumanMessage(user_input)
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
    # HTTP.Post('get', answer.content)