import ibm_db

# Use the default local connection details from your extension setup
dsn_hostname = "localhost"
dsn_port = "50000"       # Check your VS Code Db2 extension details if port differs
dsn_database = "TESTDB"
dsn_uid = "db2inst1"
dsn_pwd = "1234"  # <-- Put your real password here

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
    print("SUCCESS: Connected to local IBM Db2!")
    
    # Run a quick test query
    stmt = ibm_db.exec_immediate(conn, "SELECT 1 FROM SYSIBM.SYSDUMMY1")
    result = ibm_db.fetch_assoc(stmt)
    print("Test query result:", result)
    
    ibm_db.close(conn)
except Exception as e:
    print("Connection failed:", e)