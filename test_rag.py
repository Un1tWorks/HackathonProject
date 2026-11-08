import ibm_db
import random

dsn_hostname = "localhost"
dsn_port = "50000"
dsn_database = "TESTDB"
dsn_uid = "db2inst1"
dsn_pwd = "1234"  # <-- Put your real password

dsn = (
    f"DATABASE={dsn_database};"
    f"HOSTNAME={dsn_hostname};"
    f"PORT={dsn_port};"
    f"PROTOCOL=TCPIP;"
    f"UID={dsn_uid};"
    f"PWD={dsn_pwd};"
)

try:
    conn = ibm_db.connect(dsn, "", "")
    print("SUCCESS: Connected to Db2 for RAG test!")

    doc_title = "HR_Remote_Work_Policy_2026.pdf"
    page_num = 3
    chunk_content = "Employees are permitted to work remotely up to 3 days per week with prior manager approval. Core collaboration hours are 10 AM to 3 PM."
    dept = "HR"
    clearance = 1
    
    # Generate mock 768-dim vector string
    mock_vector = "[" + ",".join([str(round(random.uniform(-1, 1), 4)) for _ in range(768)]) + "]"

    # Notice the updated VECTOR(?, 768, FLOAT32) syntax matching Db2 requirements
    insert_sql = """
        INSERT INTO document_chunks (document_title, page_number, chunk_text, department, clearance_level, embedding)
        VALUES (?, ?, ?, ?, ?, VECTOR(?, 768, FLOAT32))
    """
    
    stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(stmt, 1, doc_title)
    ibm_db.bind_param(stmt, 2, page_num)
    ibm_db.bind_param(stmt, 3, chunk_content)
    ibm_db.bind_param(stmt, 4, dept)
    ibm_db.bind_param(stmt, 5, clearance)
    ibm_db.bind_param(stmt, 6, mock_vector)
    
    ibm_db.execute(stmt)
    print("SUCCESS: Inserted sample document chunk into Db2 with vector!")

    # Query back results
    query_sql = "SELECT id, document_title, chunk_text FROM document_chunks FETCH FIRST 5 ROWS ONLY"
    stmt_q = ibm_db.exec_immediate(conn, query_sql)
    
    print("\n--- Current Chunks in Db2 Database ---")
    result = ibm_db.fetch_assoc(stmt_q)
    while result:
        print(f"ID: {result['ID']} | Doc: {result['DOCUMENT_TITLE']}")
        print(f"Snippet: {result['CHUNK_TEXT']}\n")
        result = ibm_db.fetch_assoc(stmt_q)

    ibm_db.close(conn)

except Exception as e:
    print("RAG test execution failed:", e)