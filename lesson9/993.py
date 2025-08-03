def get_postgres_conn_params():
    """
    回傳 PostgreSQL 連線環境參數樣板。
    """
    return {
        'host': 'localhost',      # 資料庫主機位址
        'port': 5432,             # 連接埠號
        'database': 'your_db',    # 資料庫名稱
        'user': 'your_user',      # 使用者名稱
        'password': 'your_pass'   # 密碼
    }


import psycopg2

def create_postgres_connection(host, port, database, user, password):
    """
    建立並回傳 PostgreSQL 連線物件。
    """
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='postgres',
            user='postgres',
            password='raspberry'
        )
        print("連線成功！")
        return conn
    except Exception as e:
        print(f"連線失敗: {e}")
        return None
