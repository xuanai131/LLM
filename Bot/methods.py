from langchain_community.document_loaders.pdf import UnstructuredPDFLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.docstore.document import Document
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain.storage import InMemoryStore, LocalFileStore
from langchain.storage._lc_store import create_kv_docstore
from langchain.retrievers import ParentDocumentRetriever
import json
from pathlib import Path
from numpy.linalg import norm
from numpy import dot
import fitz  # PyMuPDF
import base64
import barcode
from barcode.writer import ImageWriter
import random
import string


from langchain.retrievers import ParentDocumentRetriever
from typing import List
from langchain_core.callbacks import (
    CallbackManagerForRetrieverRun,
)
from langchain.docstore.document import Document
import ast  
import uuid
import re
import unicodedata
from Global_variable import *
from table_handle import *



class CustomParentDocumentRetriever(ParentDocumentRetriever):
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        # print('/////////////////////////////////////')
        """Get documents relevant to a query.
        Args:
            query: String to find relevant documents for
            run_manager: The callbacks handler to use
        Returns:
            List of relevant documents
        """
        # print('Query: ', query)
        if self.search_type == 'mmr':
            # print('max_marginal_relevance_search')
            sub_docs = self.vectorstore.max_marginal_relevance_search(
                query, **self.search_kwargs
            )
        else:
            # print('similarity_search   ', self.search_kwargs)
            sub_docs = self.vectorstore.similarity_search(query, **self.search_kwargs)
            # print(len(sub_docs))
        # for doc in sub_docs:
            # print(doc.page_content)
        # We do this to maintain the order of the ids that are returned
        context = {}
        
        for d in sub_docs:
            if self.id_key in d.metadata and d.metadata[self.id_key] not in list(context.keys()):
                context[d.metadata[self.id_key]] = d.page_content
                # ids.append(d.metadata[self.id_key])
            else:
                context[d.metadata[self.id_key]] += '\n\n' + d.page_content
        ids = list(context.keys())
        docs = self.docstore.mget(ids)
        # for doc in docs:
        #     print(doc.page_content)
        result = []
        for i in range(len(docs)):
            if docs[i] is not None:
                # print('////////': d)
                dict = ast.literal_eval(docs[i].page_content)
                dict['Nội dung đầu sách'] = context[ids[i]]
                result.append(Document(str(dict)))
        # result = [d for d in docs if d is not None]
        print('Retriever result: ', result)
        return result

class RETRIEVER_CONFIG:
    def  __init__(self, ):
        self.parent_splitter = None
        self.child_splitter = None
        self.retriever_type = 'Custom'
        
def pdf_page_to_base64(pdf_path, page_number=0): # Extract the first page of pdf and convert it into base64 image
    pdf_document = fitz.open(pdf_path)
    # Extract the page
    page = pdf_document[page_number]
    # Convert the page to an image
    image = page.get_pixmap()
    # Convert the image to a base64 string
    image_bytes = image.tobytes("png", "RGB")
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    pdf_document.close()
    
    return base64_image

def generate_barcode(ID, filename): # Generate barcode from ID
    # Generate the barcode object
    barcode_class = barcode.get_barcode_class('code128')
    barcode_instance = barcode_class(ID, writer=ImageWriter())
    
    # Save the barcode image
    barcode_instance.save(filename)
    
def generate_unique_id(existing_ids): # Generate unique ID
    while True:
        new_id = ''.join(random.choices(string.ascii_letters + string.digits, k=9))
        if new_id not in existing_ids:
            return new_id
    
    
    
class DATABASE:
    def __init__(self, db_path, embedding, parent_path=None, retriever_config:RETRIEVER_CONFIG=None):
        self.db_path = db_path
        self.parent_path = parent_path
        self.retriever_config = retriever_config
        self.db = Chroma(collection_name="split_parents", persist_directory=db_path, embedding_function=embedding)
        if retriever_config.parent_splitter is None:
            self.parent_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap= 20, separators=[" {'"])
        else:
            self.parent_splitter = retriever_config.parent_splitter
        if retriever_config.child_splitter is None:
            self.child_splitter = RecursiveCharacterTextSplitter(
                separators=["\n","\n\n" "\\n", "\\n\\n", '",', '. '],
                chunk_size=120,
                chunk_overlap=20,
                length_function=len,
                is_separator_regex=False,
            )
        else:
            self.child_splitter = retriever_config.child_splitter
            
        self.store = self.initial_store()
        self.retriever = self.initial_retriever()
        self.existing_ids = set()
        
    def fix_invalid_characters(self, text):
        # Replace invalid characters with hyphen '-'
        cleaned_text = ''.join(char if unicodedata.category(char)[0] != 'C' else '-' for char in text)
        return cleaned_text

    def initial_store(self, ):
        fs = LocalFileStore(self.parent_path)
        store = create_kv_docstore(fs)
        return store
    
    def initial_retriever(self, ):
        if self.retriever_config.retriever_type == "Custom":
            retriever = CustomParentDocumentRetriever(
                vectorstore=self.db,
                docstore=self.store,
                child_splitter=self.child_splitter,
                parent_splitter=self.parent_splitter
            )
        elif self.retriever_config.retriever_type == "NoCustom":
            retriever = ParentDocumentRetriever(
                vectorstore=self.db,
                docstore=self.store,
                child_splitter=self.child_splitter,
                parent_splitter=self.parent_splitter
            )
        return retriever
    
    def insert_document(self, file_path, chunk_size=1000, chunk_overlap=0, jq_schema=None):
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
            text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            texts = text_splitter.split_documents(documents)
        elif file_format == 'docx':
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            texts = text_splitter.split_documents(documents)
        else:
            print(f'This function does not support {file_format} file format.')
            return
        # self.db.add_documents(texts)
        self.retriever.add_documents(texts, ids=None)
        
    def insert_processed_texts(self, documents, chunk_size=1000, chunk_overlap=0):
        text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        texts = text_splitter.split_documents(documents)
        self.retriever.add_documents(texts, ids=None)
        
        
    def add_info_to_database(self, ID, name_of_book, kind_of_book, shelve, cover_image):
        # Books table
        InsertToBookTable(ID,name_of_book,None,kind_of_book,None,None,shelve,cover_image)
        # Book items table
        ran = random.randint(1, 6)
        for i in range(ran):
            barcode = generate_unique_id(self.existing_ids)
            self.existing_ids.add(barcode)
            filename = AbsoluteBotPath+f'/Knowledge/Barcode/{name_of_book}-{barcode}.png'
            generate_barcode(barcode, filename)
            InsertToBookItemTable(barcode,ID)
        
    def insert_book(self, json_file: str, jq_schema, ids=None):
        documents = json.loads(Path(json_file).read_text())[jq_schema]
        if ids is None:
            doc_ids = [str(uuid.uuid4()) for _ in documents]
        else:
            if len(documents) != len(ids):
                raise ValueError(
                    "Got uneven list of documents and ids. "
                    "If `ids` is provided, should be same length as `documents`."
                )
            doc_ids = ids
        docs = []
        for idx in range(len(documents)):
            child_doc_file_path = AbsoluteBotPath + documents[idx]['Nội dung đầu sách']
            try:
                try:
                    pdf_loader = UnstructuredPDFLoader(child_doc_file_path)
                    child_doc = pdf_loader.load()
                except:
                    pdf_loader = PyMuPDFLoader(child_doc_file_path,extract_images=True)
                    child_doc = pdf_loader.load()
                text = ''
                for doc in child_doc:
                    text += doc.page_content
                text = re.sub(r'\.{6,}', '-', text)  #Repalce multiple dot with '-'
                text = self.fix_invalid_characters(text)
                print(".....  Adding ", documents[idx]['Nội dung đầu sách'], '  .....')
                documents[idx]['Nội dung đầu sách'] = text
                # Add to parents
                self.retriever.docstore.mset([(doc_ids[idx], Document(str(documents[idx])))])
                print(documents[idx])
                # Add info to database
                base64_img = pdf_page_to_base64(child_doc_file_path)
                self.add_info_to_database(idx+1, documents[idx]['Tên sách'], documents[idx]['Loại sách'], documents[idx]['Vị trí'], base64_img)
                # child_doc[0].page_content = text
                
                _id = doc_ids[idx]
                sub_docs = self.child_splitter.split_documents([Document(str(documents[idx]))])
                if self.retriever.child_metadata_fields is not None:
                    for _doc in sub_docs:
                        _doc.metadata = {
                            k: _doc.metadata[k] for k in self.retriever.child_metadata_fields
                        }
                for _doc in sub_docs:
                    _doc.metadata[self.retriever.id_key] = _id
                docs.extend(sub_docs)
            except:
                pass
        self.retriever.vectorstore.add_documents(docs)

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