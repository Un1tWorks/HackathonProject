import os
import sys
import tempfile
import nltk
import streamlit as st
from dotenv import load_dotenv

# Set up NLTK to work within Streamlit's restricted cloud environment
nltk_data_dir = os.path.join(tempfile.gettempdir(), "nltk_data")
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)

for resource in ["punkt", "punkt_tab", "stopwords"]:
    try:
        nltk.download(resource, download_dir=nltk_data_dir, quiet=True)
    except Exception:
        pass

# Disable tokenizer warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

# Load environment variables from local .env file
load_dotenv()

# Safely check Streamlit Secrets first; if missing locally, fall back to .env variables
try:
    groq_api_key = st.secrets.get("Hackathonkey") or os.getenv("Hackathonkey")
except Exception:
    groq_api_key = os.getenv("Hackathonkey")

try:
    DB2_DATABASE = st.secrets.get("DB2_DATABASE") or os.getenv("DB2_DATABASE", "TESTDB")
    DB2_HOSTNAME = st.secrets.get("DB2_HOSTNAME") or os.getenv("DB2_HOSTNAME", "localhost")
    DB2_PORT = st.secrets.get("DB2_PORT") or os.getenv("DB2_PORT", "50000")
    DB2_UID = st.secrets.get("DB2_UID") or os.getenv("DB2_UID", "db2inst1")
    DB2_PWD = st.secrets.get("DB2_PWD") or os.getenv("DB2_PWD", "")
except Exception:
    DB2_DATABASE = os.getenv("DB2_DATABASE", "TESTDB")
    DB2_HOSTNAME = os.getenv("DB2_HOSTNAME", "localhost")
    DB2_PORT = os.getenv("DB2_PORT", "50000")
    DB2_UID = os.getenv("DB2_UID", "db2inst1")
    DB2_PWD = os.getenv("DB2_PWD", "")
    
st.set_page_config(
    page_title="DocuSense - IBM Smart Librarian",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 DocuSense: Onboarding Smart Librarian")
st.caption("Your 24/7 AI assistant for company documentation, onboarding questions, and guidelines.")

if not groq_api_key:
    st.error("Missing GROQ_API_KEY! Please add it to Streamlit Secrets or environment variables.")
    st.stop()

# Import LlamaIndex and IBM Db2 dependencies
from llama_index.core import VectorStoreIndex, Settings, SimpleDirectoryReader, StorageContext
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import ibm_db
from llama_index.vector_stores.db2 import DB2LlamaVS, DistanceStrategy

# 1. Initialize the correct LLM and Embedding Model
global_llm = Groq(
    model="openai/gpt-oss-120b",
    api_key=groq_api_key
)
global_embed = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# 2. Register models globally in LlamaIndex Settings
Settings.llm = global_llm
Settings.embed_model = global_embed

@st.cache_resource(show_spinner="Connecting to IBM Db2 and initializing AI Engine...")
def load_rag_engine():
    # Construct the Db2 connection string
    conn_str = (
        f"DATABASE={DB2_DATABASE};"
        f"HOSTNAME={DB2_HOSTNAME};"
        f"PORT={DB2_PORT};"
        f"PROTOCOL=TCPIP;"
        f"UID={DB2_UID};"
        f"PWD={DB2_PWD};"
    )
    
    # Establish connection using ibm_db
    connection = ibm_db.connect(conn_str, "", "")
    if not connection:
        raise RuntimeError("Failed to establish connection to IBM Db2 database.")

    # Initialize Db2 Vector Store via DB2LlamaVS
    vector_store = DB2LlamaVS(
        client=connection,
        table_name="docusense_embeddings",
        distance_strategy=DistanceStrategy.COSINE
    )
    
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Check if documents need to be ingested or loaded from existing vector table
    if os.path.exists("./data") and os.listdir("./data"):
        documents = SimpleDirectoryReader("./data").load_data()
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

    # 3. Create and return the Query Engine
    return index.as_query_engine(
        similarity_top_k=3
    )

# Load the engine safely
try:
    query_engine = load_rag_engine()
except Exception as e:
    st.error(f"**Database or Engine Initialization Failed:** `{type(e).__name__}`: {str(e)}")
    st.stop()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your DocuSense onboarding assistant powered by IBM Db2. How can I help you settle in today?"}
    ]

# Render existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user query
if user_query := st.chat_input("Ex: What are the remote work guidelines and benefit details?"):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Searching company knowledge base..."):
            try:
                # Query the RAG engine
                response = query_engine.query(user_query)
                st.markdown(str(response))
                
                # Display Source Citations if available
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
                # Graceful Error Handling
                error_msg = f"**Query Execution Failed:** `{type(e).__name__}`: {str(e)}"
                st.error(error_msg)