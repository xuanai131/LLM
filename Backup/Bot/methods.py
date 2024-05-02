from langchain_community.document_loaders.pdf import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.docstore.document import Document
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
import json
from pathlib import Path
from numpy.linalg import norm
from numpy import dot



class DATABASE:
    def __init__(self, db_path, embedding):
        self.db_path = db_path
        self.db = Chroma(persist_directory=db_path, embedding_function=embedding)
        self.len_db = 0
        
    def insert_document(self, file_path, jq_schema=None):
        file_format = file_path.split('.')[-1]
        if file_format == 'pdf':
            pdf_loader = UnstructuredPDFLoader(file_path)
            pdf_pages = pdf_loader.load_and_split()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
            texts = text_splitter.split_documents(pdf_pages)
        elif file_format == 'json':
            documents = json.loads(Path(file_path).read_text())
            txts = [str(i) for i in list(documents[jq_schema])]
            texts = [Document(page_content=txt, metadata={"source": file_path}) for txt in txts]
        elif file_format == 'csv':
            loader = CSVLoader(file_path=file_path)
            texts = loader.load()
        elif file_format == 'txt':
            loader = TextLoader(file_path)
            documents = loader.load()
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            texts = text_splitter.split_documents(documents)
        else:
            print(f'This function does not support {file_format} file format.')
            return
        self.db.add_documents(texts)
        self.len_db += len(texts)
        
    def similarity_search(self, query, k=4):
        return self.db.similarity_search_with_score(query, k)
    
    
    
class history_conversation:
    def __init__(self,turn_chat=2):
        self.turn_chat = turn_chat
        self.history_query = []
        self.history_answer = []
        self.base_history = []

    def add_turn_to_history(self, query, answer):
        self.history_query.append(query)
        self.history_answer.append(answer)
    def add_to_history(self,message):
        self.base_history.append(message)

    def get_two_latest_query(self):
        return self.history_query[-self.turn_chat:]
    
    def calculate_similarity(self, a, b):
        return dot(a, b)/(norm(a)*norm(b))
    
    def return_history_chat(self):
        history_context = ""
        answers = self.history_answer[-self.turn_chat:]
        for index,query in enumerate(self.history_query[-self.turn_chat:]):
            history_context += "Question: " + query + "\n" + "Answer: " + answers[index] + "\n"
        return history_context