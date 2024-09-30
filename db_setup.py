import sqlite3
import os

def create_database():
    # Get the path of the current project directory (where the script is running)
    project_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the path to the db directory
    db_dir = os.path.join(project_dir, 'db')

    # Ensure the db directory exists
    os.makedirs(db_dir, exist_ok=True)

    # Define the path to the database file
    db_path = os.path.join(db_dir, 'seo_data.db')

    # Create a connection to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the URLs table to store metadata about each page
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            title TEXT,
            meta_description TEXT,
            source TEXT
        )
    ''')

    # Create the Headers table to store h1, h2, h3 content for each page
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS headers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            header_text TEXT NOT NULL,
            url_id INTEGER NOT NULL,
            FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE
        )
    ''')

    # Create the Body table to store raw body text for NLP (if needed in the future)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS body (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            body_text TEXT,
            url_id INTEGER NOT NULL,
            FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE
        )
    ''')

    # Create the Keywords table to store extracted keywords and their frequencies
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            frequency INTEGER,
            relevance_score REAL,
            url_id INTEGER NOT NULL,
            FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()