import os
import sys
import tempfile
import nltk
import streamlit as st
from dotenv import load_dotenv

# NLTK setup for Streamlit compatibility
nltk_data_dir = os.path.join(tempfile.gettempdir(), "nltk_data")
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)

for resource in ["punkt", "punkt_tab", "stopwords"]:
    try:
        nltk.download(resource, download_dir=nltk_data_dir, quiet=True)
    except Exception:
        pass

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

load_dotenv()
groq_api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

st.set_page_config(
    page_title="IBM Assistant",
    page_icon="💻",
    layout="centered"
)

st.title("💻 IBM Support & Strategy AI")
st.caption("Ask questions regarding IBM technologies, cloud strategies, or documentation.")

if not groq_api_key:
    st.error("Missing GROQ_API_KEY! Please check your .env file or Streamlit Secrets.")
    st.stop()

from llama_index.core import VectorStoreIndex, Settings, SimpleDirectoryReader, StorageContext
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

# Initialize LLM and Embedding Model
global_llm = Groq(
    model="openai/gpt-oss-120b", # Active high-performance Groq model
    api_key=groq_api_key
)
global_embed = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

Settings.llm = global_llm
Settings.embed_model = global_embed

@st.cache_resource(show_spinner="Initializing IBM Vector Database...")
def load_rag_engine():
    db_path = "./chroma_db"
    chroma_client = chromadb.PersistentClient(path=db_path)
    chroma_collection = chroma_client.get_or_create_collection("ibm_docs")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    if chroma_collection.count() == 0:
        documents = SimpleDirectoryReader("./data").load_data()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=storage_context,
            embed_model=global_embed
        )
    else:
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            embed_model=global_embed
        )

    return index.as_query_engine(similarity_top_k=3)

query_engine = load_rag_engine()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I help you with IBM technologies or documents today?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_query := st.chat_input("Ex: What are IBM's cloud architecture standards?"):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Searching IBM documentation..."):
            try:
                response = query_engine.query(user_query)
                st.markdown(str(response))
                
                if hasattr(response, "source_nodes") and response.source_nodes:
                    with st.expander("📄 View Source Citations"):
                        for i, node in enumerate(response.source_nodes):
                            file_name = node.node.metadata.get("file_name", "Document")
                            page_num = node.node.metadata.get("page_label", "N/A")
                            score = getattr(node, "score", 0.0) or 0.0
                            snippet = node.node.get_content()[:200].replace("\n", " ")
                            st.write(f"**[{i+1}] {file_name} (Page {page_num})** — *Match Score: {score:.4f}*")
                            st.caption(f'"{snippet}..."')

                st.session_state.messages.append({"role": "assistant", "content": str(response)})

            except Exception as e:
                st.error(f"**Query Execution Failed:** `{type(e).__name__}`: {str(e)}")