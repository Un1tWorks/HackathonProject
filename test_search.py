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
    print("SUCCESS: Connected to Db2 for Secure Search test!")

    # Simulate a user query vector (768 dimensions)
    query_vector = "[" + ",".join([str(round(random.uniform(-1, 1), 4)) for _ in range(768)]) + "]"
    
    # Simulate a user's security clearance level (e.g., Employee with clearance level 1)
    user_clearance = 1

    # Db2 native vector search query using VECTOR_DISTANCE with COSINE metric 
    # plus secure RBAC filtering (clearance_level <= user_clearance)
    search_sql = """
        SELECT id, document_title, chunk_text, clearance_level,
               VECTOR_DISTANCE(embedding, VECTOR(?, 768, FLOAT32), COSINE) AS distance
        FROM document_chunks
        WHERE clearance_level <= ?
        ORDER BY distance ASC
        FETCH FIRST 3 ROWS ONLY
    """
    
    stmt = ibm_db.prepare(conn, search_sql)
    ibm_db.bind_param(stmt, 1, query_vector)
    ibm_db.bind_param(stmt, 2, user_clearance)
    
    ibm_db.execute(stmt)
    
    print(f"\n--- Secure Vector Search Results (User Clearance <= {user_clearance}) ---")
    result = ibm_db.fetch_assoc(stmt)
    
    if not result:
        print("No authorized chunks found.")
    while result:
        print(f"Match ID: {result['ID']} | Doc: {result['DOCUMENT_TITLE']} | Clearance: {result['CLEARANCE_LEVEL']}")
        print(f"Distance Score: {result['DISTANCE']}")
        print(f"Snippet: {result['CHUNK_TEXT']}\n")
        result = ibm_db.fetch_assoc(stmt)

    ibm_db.close(conn)

except Exception as e:
    print("Search test execution failed:", e)