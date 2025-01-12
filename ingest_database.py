from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from uuid import uuid4
import openai

# import the .env file
from dotenv import load_dotenv
load_dotenv()

# configuration
DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

# initiate the embeddings model
openai.api_key = "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"

# initiate the embeddings model
embeddings_model = OpenAIEmbeddings(openai_api_key=openai.api_key, model="text-embedding-3-large")


# initiate the vector store
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH,
)

# loading the PDF document
loader = PyPDFDirectoryLoader(DATA_PATH)

raw_documents = loader.load()

# splitting the document
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

# creating the chunks
chunks = text_splitter.split_documents(raw_documents)

# creating unique ID's
uuids = [str(uuid4()) for _ in range(len(chunks))]

# adding chunks to vector store
vector_store.add_documents(documents=chunks, ids=uuids)