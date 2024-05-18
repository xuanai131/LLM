from os import system
import speech_recognition as sr
import soundfile as sf
import sounddevice as sd
import wave
import time
import threading
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import sys
sys.path.append("../")
import API_keys
import Helper_Utilities
from Voice_handle import VoiceHandle
from colorama import Fore, Back, Style
from openai import OpenAI
client = OpenAI()
i = 0

OpenAIHistoryConversation = []
graph = Helper_Utilities.CreateGraph(OpenAIHistoryConversation)

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
def get_Chat_response(text:str) -> str:
    print('...Generating answer...')
    query = HumanMessage(text)
    OpenAIHistoryConversation.append(query)
    inputs = {
        # "history" : [],
        "messages": OpenAIHistoryConversation
    }
    answer = run_graph(inputs)
    OpenAIHistoryConversation.append(answer)
    return answer.content

voicehandle = VoiceHandle(wake_words=['porcupine'], get_chat_response_func=get_Chat_response)    
voicehandle.run()
while True:
    time.sleep(0.5)