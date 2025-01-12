import time
import openai
import gradio as gr
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

# import the .env file
load_dotenv()

# configuration
DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

# Set the OpenAI API key
openai.api_key = "your api key"

# initiate the embeddings model
embeddings_model = OpenAIEmbeddings(openai_api_key=openai.api_key, model="text-embedding-3-large")

# initiate the model
llm = ChatOpenAI(temperature=0.5, model='gpt-4', api_key=openai.api_key)

# connect to the chromadb
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH, 
)

# Set up the vectorstore to be the retriever
num_results = 5
retriever = vector_store.as_retriever(search_kwargs={'k': num_results})

# Define the function to handle the chatbot messages
def stream_response(message, history):
    # Retrieve the relevant chunks based on the question asked
    docs = retriever.get_relevant_documents(message)

    # Add all the chunks to 'knowledge'
    knowledge = ""
    for doc in docs:
        knowledge += doc.page_content + "\n\n"

    # Construct the prompt for the language model
    rag_prompt = f"""
    You are an assistant which answers questions based on knowledge provided to you.
    While answering, you don't use your internal knowledge, 
    but solely the information in the "The knowledge" section.
    You don't mention anything to the user about the provided knowledge.

    The question: {message}

    Conversation history: {history}

    The knowledge: {knowledge}
    """
    
    # Retry logic in case of rate limit error
    retries = 5
    for attempt in range(retries):
        try:
            response = llm(rag_prompt)
            return response['text']
        except openai.error.RateLimitError as e:
            if attempt < retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limit reached. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Rate limit error occurred: {e}")
                return "I am currently experiencing high demand. Please try again later."

# Define the Gradio interface to manage chat history and inputs/outputs
def chatbot_ui():
    return gr.Interface(
        fn=stream_response,
        inputs=[gr.Textbox(placeholder="Ask something...", label="Message", lines=1)],
        outputs=[gr.Chatbot()],
        live=True,
        layout='vertical',  # Improve layout for better UX
    )

# Launch the Gradio app
chatbot_ui().launch()
