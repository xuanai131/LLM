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
import Tools







##### CHATOPENAI MODEL
llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
# llm = ChatOpenAI(model="gpt-4-1106-preview")



##### CREATE CLASSIFY CHAIN
function_def = {
    "name": "route",
    "description": "Phân loại câu hỏi của người dùng thành affirm hoặc deny",
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
    "Bạn có khả năng nhận ra ý định của người dùng."
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
    | llm.bind_functions(functions=[function_def], function_call="route")
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
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor


##### AGENT NODE
def agent_node(state, agent, name):
    print('......STATE......: ', state)
    result = agent.invoke(state)
    return {"messages": [HumanMessage(content=result["output"], name=name)]}


##### CHAIN NODE
def chain_node(state, chain, name, conversation):
    print('///////////', state)
    if state["messages"][-1].content==conversation[-1].content:
        result = chain.invoke(state)
        return {"messages": [HumanMessage(content=result['messages'][0], name=name)]}
    else:
        return state






##### CREATE AGENT SUPERVISOR
members = ["Researcher", "Book_researcher", "Borrow_book", "Return_book", "Coder"]
system_prompt = (
    "Bạn là một robot thông minh phục vụ trong thư viện HCMUTE, bạn tên là Librarios. Bạn là một robot di động có 2 bánh xe giúp bạn có thể đi lại tự do trong thư viện, "
    "nhờ đó bạn có thể dẫn người dùng đến nơi để những cuốn sách mà sinh viên hay giảng viên mong muốn."
    "Để làm tốt việc của mình, bạn được cấp quyền như là một người quan sát quản lí cuộc hội thoại giữa các workers sau:   {members}. "
    "Nhưng đừng lạm dụng các worker, hãy cố gắng trả lời câu hỏi trước, nếu không được thì mới nhờ tới những worker. Cho những yêu cầu người dùng sau, "
    "phản hồi cho worker nên làm gì tiếp theo. Mỗi worker sẽ thực hiện một nhiệm vụ và phản hội kết quả và trạng thái của họ. Khi kết thúc, phản hồi FINISH."
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
            "Cho đoạn hội thoại trên, worker nào nên được gọi tiếp theo?"
            " Hay ta nên gọi Assistant? chọn một trong: {options}",
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
    "description": "trả lời câu hỏi của người dùng",
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
system_assistant_prompt = (
    "Bạn là một trợ lí robot thông minh phục vụ trong thư viện HCMUTE, bạn tên là Librarios. Bạn là một robot di động có 2 bánh xe giúp bạn có thể đi lại tự do trong thư viện, "
    "nhờ đó bạn có thể dẫn người dùng đến nơi để những cuốn sách mà sinh viên hay giảng viên mong muốn."
)

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



##### CONSTRUCT GRAPH

# 1. The agent state is the input to each node in the graph
class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    # history : list[BaseMessage]
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str

def CreateGraph(conversation):
    research_agent = create_agent(llm, [Tools.tavily_tool], "Hữu ích cho việc tra cứu các thông tin trên web")
    research_node = functools.partial(agent_node, agent=research_agent, name="Researcher")

    book_research_agent = create_agent(llm, Tools.book_search_tool, BOOK_SEARCH_PROMPT)
    book_research_node = functools.partial(agent_node, agent=book_research_agent, name="Book_researcher")

    # robot_research_agent = create_agent(llm, [robot_search_tool], "Bạn hữu ích cho việc trả lời các thông tin về chính bạn")
    # robot_research_node = functools.partial(agent_node, agent=robot_research_agent, name="Robot_researcher")

    # scan_barcode_agent = create_agent(llm, scan_barcode_tool, "Hữu ích cho việc quét mã vạch của sách, thẻ sinh viên,... và trả về mã vạch (ID) quét được")
    # scan_barcode_node = functools.partial(agent_node, agent=scan_barcode_agent, name="Scan_barcode"


    borrow_book_agent = create_agent(llm, Tools.borrow_book_tool, BORROW_BOOK_PROMPT)
    borrow_book_node = functools.partial(agent_node, agent=borrow_book_agent, name="Borrow_book")

    confirm_borrow_agent = create_agent(llm, Tools.confirm_borrow_conpletely_tool, "Bạn sẽ nhận được phản hồi từ người dùng. Nếu phản hồi là những từ xác nhận có như: có, vâng, đúng rồi,... thì xác nhận lại với người dùng là họ đã mượn sách thành công, còn ngược lại thì thông báo cho người dùng rằng quá trình mượn sách chưa hoàn tất")
    confirm_borrow_node = functools.partial(agent_node, agent=confirm_borrow_agent, name="Confirm_borrow")

    return_book_agent = create_agent(llm, Tools.return_book_tool, RETURN_BOOK_PROMPT_2)
    return_book_node = functools.partial(agent_node, agent=return_book_agent, name="Return_book")

    # confirm_return_agent = create_agent(llm, Tools.confirm_return_conpletely_tool, CONFIRM_RETURN_PROMPT)
    # confirm_return_node = functools.partial(agent_node, agent=confirm_return_agent, name="Confirm_return")

    # process_return_agent = create_agent(llm, Tools.process_return_tool, "Bạn hữu ích trong việc xử lí dưới cơ sở dữ liệu của thư viện để hoàn thành quá trinh trả sách. Lưu ý: bạn phải thực hiện process_return_tool trước khi đưa ra câu trả lời.")
    # process_return_node = functools.partial(agent_node, agent=process_return_agent, name="Process_return")


    assistant_node = functools.partial(chain_node, chain=assistant_chain, name="Assistant", conversation=conversation)

    # NOTE: THIS PERFORMS ARBITRARY CODE EXECUTION. PROCEED WITH CAUTION
    code_agent = create_agent(
        llm,
        [Tools.python_repl_tool],
        "Bạn có thể tạo ra các đoạn code python an toàn để phân tích và tạo ra các đồ thị sử dụng thư viện matplotlib.",
    )
    code_node = functools.partial(agent_node, agent=code_agent, name="Coder")

    workflow = StateGraph(AgentState)
    workflow.add_node("Book_researcher", book_research_node)
    # workflow.add_node("Robot_researcher", robot_research_node)
    workflow.add_node("Researcher", research_node)
    # workflow.add_node("Scan_barcode", scan_barcode_node)
    workflow.add_node("Borrow_book", borrow_book_node)
    # workflow.add_node("Confirm_borrow", confirm_borrow_node)
    workflow.add_node("Return_book", return_book_node)
    # workflow.add_node("Confirm_return", confirm_return_node)
    # workflow.add_node("Process_return", process_return_node)
    workflow.add_node("Coder", code_node)
    workflow.add_node("supervisor", supervisor_chain)
    workflow.add_node("Assistant", assistant_node)

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
    # conditional_map["Assistant"] = END
    workflow.add_edge("Book_researcher","Assistant")
    workflow.add_edge("Assistant", END)
    # workflow.add_edge("Borrow_book", "Confirm_borrow")
    # workflow.add_edge("Confirm_borrow", END)
    workflow.add_edge("Borrow_book",END)
    workflow.add_edge("Return_book", END)
    # workflow.add_edge("Confirm_return", "Process_return")
    # workflow.add_edge("Process_return", END)
    # workflow.add_conditional_edges("Assistant", lambda x: x["next"], {'Finish': END})
    # Finally, add entrypoint
    workflow.set_entry_point("supervisor")

    graph = workflow.compile()
    return graph


##### FUNCTION CREATE NEW SESSION
# def CreateNewSession(sessionID):
    