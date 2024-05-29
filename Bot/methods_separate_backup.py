from langchain_community.document_loaders.pdf import UnstructuredPDFLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
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
from langchain_core.stores import BaseStore
from langchain_text_splitters import TextSplitter
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
from Database_handle import *



class CustomParentDocumentRetriever(ParentDocumentRetriever):
    docstore2: BaseStore[str, Document]
    child_splitter: TextSplitter = None
    def _get_relevant_documents(
        self, queries: list, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        # print('/////////////////////////////////////:', query)
        
        """Get documents relevant to a query.
        Args:
            query: String to find relevant documents for
            run_manager: The callbacks handler to use
        Returns:
            List of relevant documents
        """
        result = []
        sub_docs = []
        for query in queries:
            if self.search_type == 'mmr':
                sub_doc = self.vectorstore.max_marginal_relevance_search(
                    query, **self.search_kwargs
                )
            else:
                sub_doc = self.vectorstore.similarity_search(query, **self.search_kwargs)
            # print(sub_doc)
            if sub_doc not in sub_docs:
                sub_docs.extend(sub_doc)
        print(sub_docs)
        context = {}
        for d in sub_docs:
            if d.metadata['parent_key'] == 'None':
                if d.metadata['grandparent_key'] not in list(context.keys()):
                    context[d.metadata['grandparent_key']] = []
            else:
                if d.metadata['grandparent_key'] not in list(context.keys()):
                    context[d.metadata['grandparent_key']] = []
                else:
                    context[d.metadata['grandparent_key']].append(d.metadata['parent_key'])
        print(context)
        for gpr_key, pr_key in context.items():
            if pr_key:
                content = ''
                pr_doc = self.docstore.mget(pr_key)
                print(pr_doc)
                for _ in pr_doc:
                    content += _.page_content + '\n\n'
                doc = self.docstore2.mget([gpr_key])
                print(doc)
                if doc[0] is not None:
                    dict = ast.literal_eval(doc[0].page_content)
                    dict['Nội dung đầu sách'] = content
                    result.append(Document(str(dict)))
            else:
                result.append(self.docstore2.mget([gpr_key]))

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
    def __init__(self, db_path, 
                 parent_path,
                 grandparent_path,
                 retriever_config:RETRIEVER_CONFIG=None):
        self.db_path = db_path
        self.parent_path = parent_path
        self.grandparent_path = grandparent_path
        self.document_list = set()
        self.existing_ids = set()
        self.retriever_config = retriever_config
        self.error_doc = []
        self.db = Chroma(collection_name="split_parents", persist_directory=db_path, embedding_function=OpenAIEmbeddings(chunk_size=1))
        if retriever_config.parent_splitter is None:
            self.parent_splitter = RecursiveCharacterTextSplitter(
                separators=["\n","\n\n", "\\n", "\\n\\n", '",', '. '],
                chunk_size=1024,
                chunk_overlap=120,
                length_function=len,
                is_separator_regex=False,
            )
        else:
            self.parent_splitter = retriever_config.parent_splitter
        if retriever_config.child_splitter is None:
            self.child_splitter = RecursiveCharacterTextSplitter(
                separators=["\n","\n\n", "\\n", "\\n\\n", '",', '. ', "--"],
                chunk_size=120,
                chunk_overlap=20,
                length_function=len,
                is_separator_regex=False,
            )
        else:
            self.child_splitter = retriever_config.child_splitter
            
        self.parent_store = self.initial_store(self.parent_path)
        self.grandparent_store = self.initial_store(self.grandparent_path)
        self.retriever = self.initial_retriever()
        
    def fix_invalid_characters(self, text):
        # Replace invalid characters with hyphen '-'
        cleaned_text = ''.join(char if unicodedata.category(char)[0] != 'C' else '-' for char in text)
        return cleaned_text

    def initial_store(self, path):
        fs = LocalFileStore(path)
        store = create_kv_docstore(fs)
        return store
    
    def initial_retriever(self, ):
        if self.retriever_config.retriever_type == "Custom":
            retriever = CustomParentDocumentRetriever(
                vectorstore=self.db,
                docstore=self.parent_store,
                docstore2=self.grandparent_store,
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
        
    def split_text(self, text, delimiters):
        # Escape special regex characters in delimiters and sort by length (descending) for correct matching
        escaped_delimiters = sorted([re.escape(d) for d in delimiters], key=len, reverse=True)
        # print(escaped_delimiters)
        # Create a regex pattern that matches any of the delimiters
        pattern = '|'.join(escaped_delimiters)
        # print('pattern: ', pattern)
        # Split the text using the compiled regex pattern
        result = re.split(pattern, text)
        # Filter out empty strings from the result
        result = [segment for segment in result if len(segment.strip()) >= 5]
        return result

    def add_info_to_database(self, ID, name_of_book, kind_of_book, shelve, cover_image):
        # Books table
        InsertToBookTable(ID,name_of_book,None,kind_of_book,None,None,shelve,cover_image)
        print(' - ID in database: ', ID)
        # Book items table
        ran = random.randint(1, 6)
        for i in range(ran):
            barcode = generate_unique_id(self.existing_ids)
            self.existing_ids.add(barcode)
            filename = AbsoluteBotPath+f'/Knowledge/Barcode/{name_of_book}-{barcode}.png'
            generate_barcode(barcode, filename)
            InsertToBookItemTable(barcode,ID)
    def load_doccument_list(self, ):
        temp_doc_list = SearchAllBookName()
        temp_doc_list = [name[0] for name in temp_doc_list]
        self.document_list.update(temp_doc_list)
    def load_existing_bracode(self, ):
        temp_exist_ids = SearchAllBarcode()
        temp_exist_ids = [name[0] for name in temp_exist_ids]
        self.existing_ids.update(temp_exist_ids)
    def add_to_vectordatabse(self, doc_ids, idx, documents, child_docs, child_doc_file_path):
        print(' - ID in vector_database: ', documents[idx]['ID'])
        print('_____Add to child')
        self.retriever.vectorstore.add_documents(child_docs) # Add to child
        print('_____Add to parents')
        self.retriever.docstore.mset([(doc_ids[idx], Document(str(documents[idx])))]) # Add to parents
        print('_____Add info to database')
        base64_img = pdf_page_to_base64(child_doc_file_path) # Add info to database
        self.add_info_to_database(documents[idx]['ID'], documents[idx]['Tên sách'], documents[idx]['Loại sách'], documents[idx]['Vị trí'], base64_img)
        self.document_list.add(child_doc_file_path.split('/')[-1])
    def insert_book(self, json_file: str, jq_schema, ids=None):
        if len(self.existing_ids) < 1:
            self.load_existing_bracode()
        if len(self.document_list) < 1:
            self.load_doccument_list()
            
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
        
        for idx in range(len(documents)):
            print(f'------------------------ {idx} -----------------------------')
            child_doc_file_path = AbsoluteBotPath + documents[idx]['Nội dung đầu sách']
            # Check if file already add to vector database
            if child_doc_file_path.split('/')[-1] in self.document_list:
                continue
            # try:
            print('_Load PDF file')
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
            print(".......... Adding ", documents[idx]['Nội dung đầu sách'], ' ..........')
            # documents[idx]['Nội dung đầu sách'] = text
            print(documents[idx])
            child_docs = [Document(documents[idx]['Tên sách'], metadata = {'grandparent_key': doc_ids[idx], 'parent_key': 'None'}),
                            Document(documents[idx]['Loại sách'], metadata = {'grandparent_key': doc_ids[idx], 'parent_key': 'None'}),
                            Document(documents[idx]['Keyword'][0], metadata = {'grandparent_key': doc_ids[idx], 'parent_key': 'None'}),
                            Document(documents[idx]['Mô tả'], metadata = {'grandparent_key': doc_ids[idx], 'parent_key': 'None'})]
            # _id = doc_ids[idx]
            parent_docs = self.child_splitter.split_documents([Document(text)])
            parentdoc_ids = [str(uuid.uuid4()) for _ in parent_docs]
            delimiters = ['.', '\n']
            print('_Split text')
            for i in range(len(parent_docs)):
                text_split_doc = self.child_splitter.split_documents([parent_docs[i]])
                parent_docs[i].metadata = {'grandparent_key': doc_ids[idx], 'parent_key': parentdoc_ids[i]}
                for _ts_doc in text_split_doc:
                    _ts_doc.metadata = {'grandparent_key': doc_ids[idx], 'parent_key': parentdoc_ids[i]}
                child_docs.extend(text_split_doc)
            # child_docs = []
            # if self.retriever.child_metadata_fields is not None:
            #     for _doc in sub_docs:
            #         _doc.metadata = {
            #             k: _doc.metadata[k] for k in self.retriever.child_metadata_fields
            #         }
            # for _doc in sub_docs:
            #     _doc.metadata[self.retriever.id_key] = _id
            # child_docs.extend(sub_docs)
            # self.retriever.vectorstore.add_documents(docs)
            # self.add_to_vectordatabse(doc_ids, idx, documents, child_docs, child_doc_file_path)
            # print(' - ID in vector_database: ', documents[idx]['ID'])
            print('_____Add to child ', len(child_docs))
            self.retriever.vectorstore.add_documents(child_docs) # Add to child
            print('_____Add to parents ', len(parent_docs))
            self.retriever.docstore.mset(list(zip(parentdoc_ids, parent_docs))) # Add to parents
            print('_____Add to grandparents ')
            self.retriever.docstore2.mset([(doc_ids[idx], Document(page_content=str(documents[idx]), metadata={'grandparent_key': doc_ids[idx]}))]) # Add to grandparents
            # print('_____Add info to database')
            # base64_img = pdf_page_to_base64(child_doc_file_path) # Add info to database
            # self.add_info_to_database(documents[idx]['ID'], documents[idx]['Tên sách'], documents[idx]['Loại sách'], documents[idx]['Vị trí'], base64_img)
            self.document_list.add(child_doc_file_path.split('/')[-1])
            # except:
            #     print('________Error document________')
            #     self.error_doc.append(documents[idx]['Tên sách'])
            # if idx>=10:
            #     break

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