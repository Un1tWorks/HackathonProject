DocuSense: Onboarding Smart Librarian

DocuSense is an AI-powered assistant that answers questions about company documentation, onboarding materials, and internal guidelines using a local RAG pipeline.
Tech Stack

    Frontend: Streamlit

    Database / Vector Store: IBM Db2 (via IBM Db2 Developer Extension and DB2LlamaVS)

    LLM: Groq

    Embeddings: Hugging Face (bge-small-en-v1.5)

    PDF Parsing: PyMuPDF (fitz)

    Language: Python 3.11

How to Run Locally
1. Open the Project

Open the project directory in Visual Studio Code.
2. Create and Activate a Virtual Environment

Run these commands in the VS Code terminal:
Bash

python -m venv .venv
.venv\Scripts\activate

3. Install Dependencies

Install the required packages in your active environment:
Bash

pip install streamlit llama-index-core llama-index-llms-groq llama-index-embeddings-huggingface llama-index-vector-stores-db2 ibm_db_dbi pymupdf python-dotenv nltk

4. Configure Environment Variables

Create a file named .env in the root directory of your project and add your credentials:
Code snippet

Hackathonkey=your_groq_api_key_here
DB2_DATABASE=TESTDB
DB2_HOSTNAME=127.0.0.1
DB2_PORT=50000
DB2_UID=db2inst1
DB2_PWD=your_local_db2_password

5. Add Documents

Create a folder named data in your project root (./data/) and put your target PDF or text files inside it.
6. Run the Application

Start the local Streamlit server:
Bash

streamlit run app.py