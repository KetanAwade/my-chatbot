import os
import gradio as gr
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import webbrowser

from dotenv import load_dotenv

# Load API key
load_dotenv()

# ── 1. Load and Process Resume ──────────────────
def load_resume():
    # Load PDF
    loader = PyPDFLoader("C:/Users/Admin/OneDrive/Desktop/My ChatBot/data/Ketan_Awade_Resume_Duckcreek.pdf")
    documents = loader.load()

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    return chunks

# ── 2. Create Vector Database ───────────────────
def create_vectorstore(chunks):
    # Free HuggingFace embeddings — no API key needed!
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings
    )
    return vectorstore

# ── 3. Setup AI Chain ───────────────────────────
def create_chain(vectorstore):
    # Groq LLM
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY")
    )

    # Custom prompt — tells AI who it is
    prompt_template = """
You are Ketan Awade's personal AI assistant.
You help recruiters and hiring managers learn
about Ketan's professional background.

Answer questions ONLY from the context provided.
Be professional, confident and highlight
Ketan's strengths positively.

If the answer is not in the context say:
"I don't have that specific information.
Please contact Ketan directly at
[your email here]"

Context: {context}
Question: {question}

Answer:"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    # RAG Chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_kwargs={"k": 3}
        ),
        chain_type_kwargs={"prompt": prompt}
    )
    return chain

# ── 4. Initialize Everything ────────────────────
print("Loading resume...")
chunks = load_resume()
print(f"Resume split into {len(chunks)} chunks")

print("Creating vector database...")
vectorstore = create_vectorstore(chunks)
print("Vector database ready!")

print("Setting up AI chain...")
chain = create_chain(vectorstore)
print("Ready to chat!")

# ── 5. Chat Function ────────────────────────────
def chat(message, history):
    try:
        response = chain.invoke({"query": message})
        return response["result"]
    except Exception as e:
        return f"Error: {str(e)}"

# ── 6. Gradio UI ────────────────────────────────
demo = gr.ChatInterface(
    fn=chat,
    title="👨‍💼 Chat with Ketan Awade's AI Assistant",
    description="""
    Hi! I am Ketan's AI Assistant powered by 
    LangChain + Groq. Ask me anything about 
    Ketan's experience, skills, and background!
    """,
    examples=[
        "What is Ketan's total work experience?",
        "What technical skills does Ketan have?",
        "Tell me about Ketan's current role",
        "What is Ketan's educational background?",
        "Why should we hire Ketan?"
    ],
    # theme=gr.themes.Soft()
)

if __name__ == "__main__":
    
    demo.launch(
           inbrowser=True,
           share=True     # optional public URL
    )