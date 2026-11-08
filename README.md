# HackathonProject

DocuSense is an AI-powered onboarding assistant designed for enterprises, built specifically for the Db2Hack 2026 hackathon. It serves as an on-demand, 24/7 "smart librarian" that provides new employees with instant, accurate answers to onboarding questions, guidelines, and company policies without burning team bandwidth.

---

## Table of Contents
- [Features](#features)
- [Prerequisites & Setup](#prerequisites)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Usage](#usage)

## Features
- Native Vector Storage with IBM Db2: Leverages IBM Db2’s native vector capabilities via llama-index-vector-stores-db2 and ibm_db for scalable, robust document retrieval.
- RAG Architecture (LlamaIndex): Automatically indexes company documents (.pdf, .txt) from a local data repository.
- Groq LLM Integration: Uses high-speed LLM processing (openai/gpt-oss-120b) for rapid, context-aware responses.
- Interactive Streamlit UI: A clean, responsive chat interface featuring persistent session state and an expandable Source Citations viewer for transparency and trust.

## Prerequisites
1. Clone and Navigate to the Repository

git clone <your-repository-url>
cd HackathonProject

2. Create and Activate a Python 3.11 Virtual Environment

py -3.11 -m venv .venv
.venv\Scripts\Activate

3. Install Dependencies

python -m pip install --upgrade pip
pip install streamlit python-dotenv nltk pymupdf llama-index-core llama-in

## Configuration

Create a .env file in the root directory of your project with your Groq API key and IBM Db2 credentials:

GROQ_API_KEY="your-groq-api-key-here"

DB2_DATABASE="BLUDB"  
DB2_HOSTNAME="your-db2-hostname.databases.appdomain.cloud"  
DB2_PORT="32733"  
DB2_UID="your-db2-username" 
DB2_PWD="your-db2-password"

## Project Structure

HackathonProject/  
│  
├── app.py              > Main Streamlit application  
├── requirements.txt    > Python package dependencies  
├── .env                > Secret environment variables (ignored by git)  
└── data/               > Folder for company onboarding documents (PDFs/TXTs)  
    └── onboarding.pdf  > Place your documents here  


## Usage

Make sure your virtual environment is active and your documents are placed inside the ./data/ folder.

Launch the Streamlit app:

streamlit run app.py


Open your browser at http://localhost:8501 and start asking questions!