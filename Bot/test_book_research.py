BOOK_SEARCH_PROMPT = """  
        You are a very helpful assistant in finding books in the library or providing information about books to users.
        You must execute the tools in order book_researcher then load_book:
        First, you use the book_researcher tool to get information about the book and return it to the user.
        Then you need to get the "ID" attribute of each book you found. Then create a list of "IDs" like: ['1', '2']
        or ['20134011','20134013']
        Next, provide that list as the "book_ids" input parameter to the load_book tool.
        Finally, execute load_book and respond to the user.
        Note: Answer in Vietnamese
"""
from Helper_Utilities import create_agent,llm
from Tools import embedding 
from methods import DATABASE
from langchain.tools.retriever import create_retriever_tool
from langchain.agents import Tool
from langchain_core.messages  import HumanMessage


from langchain_community.llms import OpenAI
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

BookInfo =  DATABASE(db_path='/var/www/html/Bot/book_info', embedding=embedding) 
book_retriever = BookInfo.db.as_retriever(
    search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.2, "k": 4}
)


def load_book(book_ids: str):
    # images = []
    # for book_id in book_ids:
    print(book_ids)
    #     images.append("data:image/jpeg;base64," + str(book_search.search_book_image_by_id(book_id)[0]))
    # return book_ids
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

retriever = BookInfo.db.as_retriever()
compressor = LLMChainExtractor.from_llm(llm)

compression_retriever = ContextualCompressionRetriever(base_compressor=compressor,
                                                       base_retriever=retriever)

compressed_docs = compression_retriever.get_relevant_documents("Tôi muốn tìm cuốn sách của tác giả nguyễn huỳnh lâm vũ")

print(compressed_docs)

# book_research_agent = create_agent(llm, book_search_tool, BOOK_SEARCH_PROMPT)
# book_research_agent.invoke({'messages': [HumanMessage("tôi muốn tìm sách của Hồ Văn Đằng")]})