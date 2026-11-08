DocuSense Architecture

This document outlines the system design, core components, and data flow of DocuSense.
System Overview

DocuSense is a Retrieval-Augmented Generation (RAG) application that connects an interactive user interface directly to a relational vector store. It processes local documents, stores vector embeddings persistently in IBM Db2, and uses a high-speed LLM via Groq to provide accurate, context-aware answers to user queries.
Component Breakdown

    Frontend Interface: Built with Streamlit to handle user sessions, chat history, input forms, and dynamic rendering of source citations.

    Document Ingestion & Parsing: Utilizes PyMuPDF (fitz) to extract clean text page-by-page from local PDF files located in the ./data/ directory.

    Embeddings & Vectorization: Converts text chunks into numerical vectors using the Hugging Face embedding model (bge-small-en-v1.5).

    Vector Database & Persistence: Uses IBM Db2 managed via the IBM Db2 Developer Extension, interacting through the ibm_db_dbi driver and LlamaIndex's DB2LlamaVS integration adapter (docusense_embeddings_v4 table).

    Inference & LLM: Powered by Groq to generate fast, accurate text responses based on retrieved document contexts.

Data Flow & Pipeline
1. Initialization and Persistence Check

    When the application starts, it establishes a connection to the local IBM Db2 database.

    It queries the docusense_embeddings_v4 table to check if vector data already exists.

    If data is found, the index is loaded directly from memory in Db2, skipping re-ingestion.

    If the table is empty, the pipeline proceeds to ingestion.

2. Ingestion Flow (Run Once)

    Raw PDF and text files in ./data/ are read page-by-page.

    Extracted text is wrapped into LlamaIndex Document objects containing file name and page number metadata.

    Documents are embedded and stored persistently inside the IBM Db2 vector table.

3. Query and Retrieval Flow

    The user inputs a natural language question through the Streamlit chat interface.

    The query text is converted into a vector embedding using the local Hugging Face model.

    A cosine similarity search (DistanceStrategy.COSINE) is executed against the IBM Db2 vector store to retrieve the top k most relevant context nodes (similarity_top_k=3).

    Retrieved contexts and the user query are sent to the Groq LLM.

    The LLM generates the final response, which is displayed alongside expandable source citations showing file names, page numbers, and match scores.

Database Persistence Design

To prevent redundant processing across application reloads, vector data is strictly decoupled from temporary application memory and persisted inside an IBM Db2 relational table (docusense_embeddings_v4). This ensures data durability and quick recovery during local development and evaluation.