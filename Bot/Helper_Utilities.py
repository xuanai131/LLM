from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
import operator
from typing import Annotated, Any, Dict, List, Optional, Sequence, TypedDict
import functools

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import API_keys
from Prompt import *
from Global_variable import *
import Tools
from colorama import Fore, Back, Style
redirect_state = "supervisor"





##### CHATOPENAI MODEL
llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
# llm = ChatOpenAI(model="gpt-4-1106-preview")



##### CREATE CLASSIFY CHAIN
classify_function_def = {
    "name": "route",
    "description": "Classify user questions into affirm or deny.",
    "parameters": {
        "title": "routeSchema",
        "type": "object",
        "properties": {
            "messages": {
                "title": "messages",
                "ouput": 'text',
                "anyOf": [
                    {"enum": ['affirm', 'deny']},
                ],
            }
        },
        "required": ["messages"],
    },
}
system_prompt = (
    "You have the ability to recognize the user's intent."
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        # MessagesPlaceholder(variable_name="history"),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

classify_chain = (
    prompt
    | llm.bind_functions(functions=[classify_function_def], function_call="route")
    | JsonOutputFunctionsParser()
)




##### CREATE AGENT FUNCTION
def create_agent(llm: ChatOpenAI, tools: list, system_prompt: str):
    # Each worker node will be given a name and some tools.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools,return_intermediate_steps=True)
    return executor


##### AGENT NODE
def agent_node(state, agent, name):
    # state.get("messages").pop()
    print('......STATE......: ', state)
    if (name == "Book_researcher"): 
        output = ""
        query = ""
        check = False
        while not check :
            print("state in each loop: ")
            result = agent.stream(state)
            for chunk in result:
                print("each step in agent stream: ",chunk)
                if chunk.get("actions") is not None:
                    if chunk.get("actions")[0].tool == "load_book":
                        check = True
                    if chunk.get("actions")[0].tool == 'book_researcher':
                        query = chunk.get("actions")[0].tool_input
                output = chunk.get("output")
            if check:
                print("last step with output: ",output)
            else:
                print(Fore.RED +"bad response: load_tool is not running")
                print(Style.RESET_ALL)
                state["messages"].pop()
                state["messages"].append(HumanMessage(content="tìm cho tôi những cuốn "+str(query)))
        return {"messages": [HumanMessage(content=output, name=name)]}
    else:
        result = agent.invoke(state)
        return {"messages": [HumanMessage(content=result["output"], name=name)]}


##### CHAIN NODE
def chain_node(state, chain, name, conversation):
    print('///////////', state)
    
    if name=="Book_researcher_inspector":
        result = chain.invoke(state)
        return result
    else:
        if state["messages"][-1].content==conversation[-1].content:
            result = chain.invoke(state)
            return {"messages": [HumanMessage(content=result['messages'][0], name=name)]}
        else:
            return state






##### CREATE AGENT SUPERVISOR
members = ["Researcher", "Book_researcher", "Self_nkowledge_search", "Borrow_book", "Return_book", "Coder"]
system_prompt = (
    "You are an intelligent robot serving in the HCMUTE library, your name is Librarios. "
    "you can guide users to the location of the books that students or lecturers desire."
    "To perform your duties well, you are granted authority as an observer managing the conversation between the following workers: {members}."
    "Note: for requests related to books, prioritize using the Book_researcher worker over the Researcher. For the following user requests, "
    "provide feedback to the worker on what to do next. Each worker will perform a task and respond with their results and status. "
    "when The research done its task it always response with FINISH "
    "When finished, respond with FINISH."
    )
# Our team supervisor is an LLM node. It just picks the next agent to process
# and decides when the work is completed
options = ["Assistant"] + members
# Using openai function calling can make output parsing easier for us
function_def = {
    "name": "route",
    "description": "Select the next role.",
    "parameters": {
        "title": "routeSchema",
        "type": "object",
        "properties": {
            "next": {
                "title": "Next",
                "anyOf": [
                    {"enum": options},
                ],
            }
        },
        "required": ["next"],
    },
}
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        # MessagesPlaceholder(variable_name="history"),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            # "each worker have specific function :"
            # "*Assistant* to help the bot interact with human by natural communication when human says like :hello , thank you, sorry"
            # "*Researcher* to help answer the knowledge the need to search in the internet or any thing that book_researcher do not know"
            # "*Book_researcher* to find the infomation of the book in database, if not userful infomation in it, go to [Researcher] to find more infomation"
            # "*Self_nkowledge_search* to search and anwser the questions related to your work or library"
            # "*Borrow_book* to handle chain of action relate to borrow book"
            # "*Return_book* to handle chain of action relate to return book"
            "Based on the conversation above, which worker should be called next? "
            "Or should we call the Assistant? Choose one of: {options}."
        ),
    ]
).partial(options=str(options), members=", ".join(members))


supervisor_chain = (
    prompt
    | llm.bind_functions(functions=[function_def], function_call="route")
    | JsonOutputFunctionsParser()
)



##### CREATE ASSISTANT AGENT
function_def = {
    "name": "route",
    "description": "Helpfull to anwser questions of users",
    "parameters": {
        "title": "routeSchema",
        "type": "object",
        "properties": {
            "messages": {
                "title": "messages",
                "ouput": 'text',
            }
        },
        "required": ["messages"],
    },
}

system_assistant_prompt = (ASSISTANT_PROMPT)
assistant_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_assistant_prompt),
        # MessagesPlaceholder(variable_name="history"),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

assistant_chain = (
    assistant_prompt
    | llm.bind_functions(functions=[function_def], function_call="route")
    | JsonOutputFunctionsParser()
)
classify_function_def = {
    "name": "route",
    "description": "Classify the response to be good or bad",
    "parameters": {
        "title": "routeSchema",
        "type": "object",
        "properties": {
            "inspector": {
                "title": "inspector",
                "ouput": 'text',
                "anyOf": [
                    {"enum": ['yes', 'no']},
                ],
            }
        },
        "required": ["inspector"],
    },
}
book_research_inspector_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", (BOOK_RESEARCHER_INSPECTOR_PROMPT)),
        # MessagesPlaceholder(variable_name="history"),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
book_research_inspector_chain = (
    book_research_inspector_prompt 
    | llm.bind_functions(functions=[classify_function_def], function_call="route")
    | JsonOutputFunctionsParser()
)
interrupt_function_def = {
    "name": "route",
<<<<<<< HEAD
    "description": "the answer would be yes or no",
=======
    "description": "Check the user request interrupt event to be yes or no",
>>>>>>> b14832f28457404fc66e4196e984245729c4837a
    "parameters": {
        "title": "routeSchema",
        "type": "object",
        "properties": {
            "messages": {
                "title": "messages",
                "output": 'text',
                "anyOf": [
                    {"enum": ['yes', 'no']},
                ],
            }
        },
        "required": ["messages"],
    },
}
book_return_interrupt_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", (BOOK_RETURN_INTERRUPT_PROMPT)),
        # MessagesPlaceholder(variable_name="history"),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
book_return_interrupt_chain = (
<<<<<<< HEAD
    book_return_interrupt_prompt 
=======
    book_research_inspector_prompt 
>>>>>>> b14832f28457404fc66e4196e984245729c4837a
    | llm.bind_functions(functions=[interrupt_function_def], function_call="route")
    | JsonOutputFunctionsParser()
)
##### CONSTRUCT GRAPH

# 1. The agent state is the input to each node in the graph
class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    # history : list[BaseMessage]
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str
    inspector:str

def read_state():
    # Open the file in read mode
    with open(AbsoluteBotPath+'/state', 'r') as file:
        # Read the entire file contents into a variable
        file_contents = file.read()
        print(file_contents)
    return file_contents
def write_state(state):
    with open(AbsoluteBotPath+'/state', 'w') as file:
    # Write new content to the file
        file.write(state)
def redirect_fun(data):
    res = {}
    state = read_state()
    res["next"] = state
    print("from redirect node ",res)

    # last_index = len(data["messages"])
    # if (last_index>0) :
    #     data["messages"].pop(last_index-1)
    # del data["messages"]
    return res
def CreateGraph(conversation):
    research_agent = create_agent(llm, [Tools.tavily_tool], "Useful for looking up information on the web.")
    research_node = functools.partial(agent_node, agent=research_agent, name="Researcher")

<<<<<<< HEAD
    # book_research_agent = create_agent(llm, Tools.book_search_tool, BOOK_SEARCH_PROMPT)
    # book_research_node = functools.partial(agent_node, agent=book_research_agent, name="Book_researcher")
    from langchain.chains import RetrievalQA
    book_research_chain = RetrievalQA.from_chain_type(llm=llm, chain_type='stuff', retriever= Tools.BookInfo.retriever, return_source_documents=True, verbose=True, input_key="messages")
    book_research_node = functools.partial(chain_node, chain=book_research_chain, name="Book_researcher", conversation=conversation)
=======
    book_research_agent = create_agent(llm, Tools.book_search_tool, BOOK_SEARCH_PROMPT1)
    book_research_node = functools.partial(agent_node, agent=book_research_agent, name="Book_researcher")
>>>>>>> b14832f28457404fc66e4196e984245729c4837a

    # robot_research_agent = create_agent(llm, [robot_search_tool], "Bạn hữu ích cho việc trả lời các thông tin về chính bạn")
    # robot_research_node = functools.partial(agent_node, agent=robot_research_agent, name="Robot_researcher")

    # scan_barcode_agent = create_agent(llm, scan_barcode_tool, "Hữu ích cho việc quét mã vạch của sách, thẻ sinh viên,... và trả về mã vạch (ID) quét được")
    # scan_barcode_node = functools.partial(agent_node, agent=scan_barcode_agent, name="Scan_barcode"


    borrow_book_agent = create_agent(llm, Tools.borrow_book_tool, BORROW_BOOK_PROMPT)
    borrow_book_node = functools.partial(agent_node, agent=borrow_book_agent, name="Borrow_book")

    confirm_borrow_agent = create_agent(llm, Tools.confirm_borrow_conpletely_tool, "You will receive feedback from the user. "
                                        "If the response is confirmation words such as: yes, okay, correct,... then confirm to the user that they have successfully borrowed the book." 
                                        "Otherwise, inform the user that the book borrowing process is not yet completed.")
    confirm_borrow_node = functools.partial(agent_node, agent=confirm_borrow_agent, name="Confirm_borrow")

    return_book_agent = create_agent(llm, Tools.return_book_tool, RETURN_BOOK_PROMPT)
    return_book_node = functools.partial(agent_node, agent=return_book_agent, name="Return_book")
    
    self_knowledge_agent = create_agent(llm, Tools.self_knowledge_tool, SELF_KNOWLEDGE_PROMPT)
    self_knowledge_node = functools.partial(agent_node, agent=self_knowledge_agent, name="Self_nkowledge_search")

    # confirm_return_agent = create_agent(llm, Tools.confirm_return_conpletely_tool, CONFIRM_RETURN_PROMPT)
    # confirm_return_node = functools.partial(agent_node, agent=confirm_return_agent, name="Confirm_return")

    # process_return_agent = create_agent(llm, Tools.process_return_tool, "Bạn hữu ích trong việc xử lí dưới cơ sở dữ liệu của thư viện để hoàn thành quá trinh trả sách. Lưu ý: bạn phải thực hiện process_return_tool trước khi đưa ra câu trả lời.")
    # process_return_node = functools.partial(agent_node, agent=process_return_agent, name="Process_return")
    book_research_inspector_node = functools.partial(chain_node, chain=book_research_inspector_chain, name="Book_researcher_inspector",conversation=conversation)

    assistant_node = functools.partial(chain_node, chain=assistant_chain, name="Assistant", conversation=conversation)

    # NOTE: THIS PERFORMS ARBITRARY CODE EXECUTION. PROCEED WITH CAUTION
    code_agent = create_agent(
        llm,
        [Tools.python_repl_tool],
        "You can create safe Python code to analyze and generate graphs using the matplotlib library.",
    )
    code_node = functools.partial(agent_node, agent=code_agent, name="Coder")
    workflow = StateGraph(AgentState)
    workflow.add_node("Book_researcher", book_research_node)
    # workflow.add_node("Robot_researcher", robot_research_node)
    workflow.add_node("Researcher", research_node)
    workflow.add_node("Self_nkowledge_search", self_knowledge_node)
    # workflow.add_node("Scan_barcode", scan_barcode_node)
    workflow.add_node("Borrow_book", borrow_book_node)
    # workflow.add_node("Confirm_borrow", confirm_borrow_node)
    workflow.add_node("Return_book", return_book_node)
    # workflow.add_node("Confirm_return", confirm_return_node)
    # workflow.add_node("Process_return", process_return_node)
    workflow.add_node("Coder", code_node)
    workflow.add_node("supervisor", supervisor_chain)
    workflow.add_node("Assistant", assistant_node)
    workflow.add_node("redirect",redirect_fun)
    workflow.add_node("Book_researcher_inspector",book_research_inspector_node)
    #2. Now connect all the edges in the graph.
    for member in members:
        # We want our workers to ALWAYS "report back" to the supervisor when done
        if member != "Borrow_book" and member != "Return_book" and member!= "Book_researcher":
            workflow.add_edge(member, "supervisor")
    # workflow.add_edge(member, "supervisor")
    # The supervisor populates the "next" field in the graph state
    # which routes to a node or finishes
    conditional_map = {k: k for k in members}
    conditional_map["Assistant"] = "Assistant"
    # conditional_map["FINISH"] = END
    workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
    redirect_map = {}
    redirect_map["Borrow_book"] = "Borrow_book"
    redirect_map["supervisor"] = "supervisor"
    redirect_map["Return_book"] = "Return_book"
    redirect_map["Book_researcher"] = "Book_researcher"
    workflow.add_conditional_edges("redirect", lambda x: x["next"], redirect_map)
    # conditional_map["Assistant"] = END
    workflow.add_edge("Book_researcher","Book_researcher_inspector")
    workflow.add_edge("Self_nkowledge_search", END)
    workflow.add_edge("Assistant", END)
    workflow.add_edge("Book_researcher_inspector",END)
    # workflow.add_edge("Borrow_book", "Confirm_borrow")
    # workflow.add_edge("Confirm_borrow", END)
    # workflow.add_edge("Borrow_book", "Book_researcher")
    workflow.add_edge("Borrow_book", END)
    workflow.add_edge("Return_book", END)
    # workflow.add_edge("Confirm_return", "Process_return")
    # workflow.add_edge("Process_return", END)
    # workflow.add_conditional_edges("Assistant", lambda x: x["next"], {'Finish': END})
    # Finally, add entrypoint
    workflow.set_entry_point("redirect")
    graph = workflow.compile()
    return graph

##### FUNCTION CREATE NEW SESSION
# def CreateNewSession(sessionID):
    