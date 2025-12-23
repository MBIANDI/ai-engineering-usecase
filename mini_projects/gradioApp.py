def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn
warnings.filterwarnings('ignore')

import os
from dotenv import load_dotenv

load_dotenv()

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

from langchain.docstore.document import Document as LangchainDocument
from typing import List
from huggingface_hub import HfFolder

import gradio as gr


## LLM
def get_llm(model_name: str= "gpt-4.1-mini") -> ChatOpenAI:
    llm = ChatOpenAI(
            model= model_name,
            temperature=1,
            #model_kwargs = {"top_p":0.2, "top_k":1},
            max_tokens=256,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    return llm

## Document loader
def document_loader(file: str) -> LangchainDocument:
    loader = PyPDFLoader(file)
    loaded_document = loader.load()
    return loaded_document

## Text splitter
def text_splitter(data, chunk_size: int=1000, chunk_overlap: int=50) -> List:
    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                        add_start_index=True,
                        separators=["\n\n", "\n", ".", " ", ""],
                    )
    chunks = text_splitter.split_documents(data)
    return chunks

## Vector db
def vector_database(chunks, model_name: str="sentence-transformers/all-mpnet-base-v2"):
    embeddings = HuggingFaceEmbeddings(model_name=model_name, encode_kwargs={
            "normalize_embeddings": True
        })
    docsearch = Chroma.from_documents(chunks, embeddings)
    return docsearch


## Retriever
def retriever(file):
    splits = document_loader(file)
    chunks = text_splitter(splits)
    vectordb = vector_database(chunks)
    retriever = vectordb.as_retriever()
    return retriever

## QA Chain
def retriever_qa(file, query):
    llm = get_llm()
    retriever_obj = retriever(file)
    prompt_template = """ Use the information from the document to answer the question at the end. If you don't know the answer, just say that you don't know, definately do not try to make up an answer.

        {context}

        Question: {question}

        """
    PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
    )
    chain_type_kwargs = {"prompt": PROMPT}
    qa = RetrievalQA.from_chain_type(llm=llm, 
                                 chain_type="stuff", 
                                 retriever=retriever_obj, 
                                 chain_type_kwargs=chain_type_kwargs, 
                                 return_source_documents=False)
    # qa = RetrievalQA.from_chain_type(llm=llm, 
    #                                 chain_type="stuff", 
    #                                 retriever=retriever_obj, 
    #                                 return_source_documents=False)
    response = qa.invoke(query)
    return response['result']

# Create Gradio interface
rag_application = gr.Interface(
    fn=retriever_qa,
    # allow_flagging=False,
    inputs=[
        gr.File(label="Upload PDF File", file_count="single", file_types=['.pdf'], type="filepath"),  
        gr.Textbox(label="Input Query", lines=2, placeholder="Type your question here...")
    ],
    outputs=gr.Textbox(label="Answer"),
    title="Cameroon touristic assistant",
    description="Upload a PDF document and ask any question. The chatbot will try to answer using the provided document."
)

# Launch the app
rag_application.launch(
    # server_name="0.0.0.0",
    # server_port=7860
)
