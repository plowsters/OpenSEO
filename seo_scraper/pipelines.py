# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import sqlite3
import spacy
from collections import Counter
from itemadapter import ItemAdapter

class SeoScraperPipeline:
    def __init__(self):
        # Initialize spaCy NLP model
        self.nlp = spacy.load('en_core_web_md')
        # Connect to the SQLite database
        self.conn = sqlite3.connect('seo_data.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Ensure the necessary tables exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS urls (
                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  url TEXT UNIQUE NOT NULL,
                                  title TEXT,
                                  meta_description TEXT,
                                  source TEXT
                               )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS headers (
                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  header_text TEXT NOT NULL,
                                  url_id INTEGER NOT NULL,
                                  FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE
                               )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS keywords (
                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  keyword TEXT NOT NULL,
                                  frequency INTEGER,
                                  relevance_score REAL,
                                  url_id INTEGER NOT NULL,
                                  FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE
                               )''')
        self.conn.commit()

    def process_item(self, item, spider):
        # Insert URL into the database
        # First, check if the URL already exists and fetch the `id` if it does
        self.cursor.execute('SELECT id FROM urls WHERE url = ?', (item['url'],))
        result = self.cursor.fetchone()

        if result:
            url_id = result[0]  # Existing URL
        else:
            # Insert the new URL and get the `url_id`
            self.cursor.execute(
                'INSERT INTO urls (url, title, meta_description, source) VALUES (?, ?, ?, ?)', 
                (item['url'], item['title'], item['meta_description'], item['source'])
            )
            self.conn.commit()
            url_id = self.cursor.lastrowid  # New URL's ID

        # Insert headers (if any)
        for header in item.get('headers', []):
            self.cursor.execute('INSERT INTO headers (header_text, url_id) VALUES (?, ?)', (header, url_id))
        self.conn.commit()

        # Perform NLP on body text for keywords (if body_text is available)
        body_text = item.get('body_text')
        if body_text:
            doc = self.nlp(body_text)
            keywords = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
            keyword_counts = Counter(keywords)

            # Store keywords in the database
            for keyword, freq in keyword_counts.items():
                self.cursor.execute(
                    'INSERT INTO keywords (keyword, frequency, url_id) VALUES (?, ?, ?)', 
                    (keyword, freq, url_id)
                )
        self.conn.commit()

        return item

    def close_spider(self, spider):
        self.conn.close()