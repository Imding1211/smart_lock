
import datetime
import sqlite3

#=============================================================================#

DB_NAME    = "line_bot_records.db"
TABLE_NAME = "line_messages"

#=============================================================================#

def init_db():
    """初始化 SQLite 資料庫：如果資料表不存在則建立。"""

    try:
        conn   = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                message_id TEXT UNIQUE NOT NULL,
                source_type TEXT NOT NULL,
                user_id TEXT,
                group_room_id TEXT,
                message_content TEXT
            );
        """)

        conn.commit()

        print(f"SQLite 資料庫 '{DB_NAME}' 初始化完成，資料表 '{TABLE_NAME}' 準備就緒。")

    except sqlite3.Error as e:
        print(f"資料庫初始化失敗: {e}")

    finally:
        if conn:
            conn.close()

#-----------------------------------------------------------------------------#

def insert_message_record(record):
    """將對話紀錄寫入資料庫。"""

    conn = None

    try:
        conn   = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(f"""
            INSERT INTO {TABLE_NAME} 
            (timestamp, message_id, source_type, user_id, group_room_id, message_content)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            record['timestamp'],
            record['message_id'],
            record['source_type'],
            record['user_id'],
            record['group_room_id'],
            record['message_content']
        ))
        
        conn.commit()

        print("訊息紀錄成功寫入資料庫。")

    except sqlite3.IntegrityError:
        print(f"訊息 ID {record['message_id']} 已存在，跳過寫入。")

    except sqlite3.Error as e:
        print(f"資料庫寫入失敗: {e}")

    finally:
        if conn:
            conn.close()

#-----------------------------------------------------------------------------#

def fetch_recent_records(user_id, minutes=10):
    """
    查詢特定 user_id 在過去指定分鐘數內的訊息紀錄。
    **已修正：直接將 TEXT 欄位內容視為 Unix Timestamp 進行數值比較。**
    
    Args:
        user_id (str): 要查詢的 LINE 使用者 ID。
        minutes (int): 查詢的時間範圍 (分鐘)。
        
    Returns:
        list: 包含查詢結果 (tuple) 的列表。
    """
    conn = None
    records = []
    
    try:
        time_limit = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
        time_limit_timestamp = int(time_limit.timestamp()) 
        
        print(f"計算出的時間限制 (現在的 Unix Timestamp - {minutes} 分鐘): {time_limit_timestamp}")
        
        conn   = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT id, timestamp, message_id, source_type, user_id, message_content 
            FROM {TABLE_NAME}
            WHERE user_id = ? 
              AND timestamp >= ?  -- 直接比較 timestamp 欄位（純數值字串）與 time_limit_timestamp
            ORDER BY timestamp DESC;
        """, (user_id, str(time_limit_timestamp))) # 注意：傳入 SQL 的參數也建議轉為字串以匹配 TEXT 欄位

        records = cursor.fetchall()
        
        print(f"成功查詢到 user_id '{user_id}' 在過去 {minutes} 分鐘內的 {len(records)} 筆紀錄。")
        
    except sqlite3.Error as e:
        print(f"資料庫查詢失敗: {e}")
        
    except Exception as e:
        print(f"時間戳記計算或處理錯誤: {e}")

    finally:
        if conn:
            conn.close()
            
    return records

#-----------------------------------------------------------------------------#

def delete_records_by_user_id(user_id):
    """
    清空指定 user_id 的所有訊息紀錄。

    Args:
        user_id (str): 要刪除的 LINE 使用者 ID。
    """
    conn = None

    try:
        conn   = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(f"""
            DELETE FROM {TABLE_NAME}
            WHERE user_id = ?;
        """, (user_id,))

        deleted_count = cursor.rowcount
        conn.commit()

        print(f"已成功刪除 user_id '{user_id}' 的 {deleted_count} 筆紀錄。")

    except sqlite3.Error as e:
        print(f"刪除資料失敗: {e}")

    finally:
        if conn:
            conn.close()
            
#=============================================================================#

if __name__ == '__main__':
    init_db()
