import sqlite3
import json
from datetime import datetime

DB_NAME = "reviews_history.db"

def init_db():
    """Create the database and tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            language TEXT,
            code TEXT,
            exec_result TEXT,
            ai_report TEXT,
            chat_history TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_review(language, code, exec_result, ai_report, chat_history):
    """Save a new code review to the database and return its ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO reviews (timestamp, language, code, exec_result, ai_report, chat_history)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        timestamp, 
        language, 
        code, 
        json.dumps(exec_result),  # Convert dict to string
        ai_report, 
        json.dumps(chat_history)  # Convert list to string
    ))
    
    review_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return review_id

def update_chat_history(review_id, chat_history):
    """Update the chat history for a specific review."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE reviews SET chat_history = ? WHERE id = ?
    ''', (json.dumps(chat_history), review_id))
    conn.commit()
    conn.close()

def get_all_reviews_summary():
    """Fetch a summary of all past reviews for the sidebar."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, timestamp, language FROM reviews ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_review_by_id(review_id):
    """Fetch all data for a specific review."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT language, code, exec_result, ai_report, chat_history FROM reviews WHERE id = ?', (review_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "language": row[0],
            "code": row[1],
            "exec_result": json.loads(row[2]),
            "ai_report": row[3],
            "chat_history": json.loads(row[4])
        }
    return None