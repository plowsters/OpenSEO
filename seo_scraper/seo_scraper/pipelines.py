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
        self.conn = sqlite3.connect('seo_data.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Create tables in SQLite for storing keywords and pages
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS urls (
                                  id INTEGER PRIMARY KEY,
                                  url TEXT UNIQUE
                               )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS keywords (
                                  id INTEGER PRIMARY KEY,
                                  keyword TEXT NOT NULL,
                                  frequency INTEGER,
                                  relevance_score REAL,
                                  url_id INTEGER,
                                  FOREIGN KEY (url_id) REFERENCES urls (id)
                               )''')
        self.conn.commit()

    def process_item(self, item, spider):
        # Insert URL into database
        self.cursor.execute('INSERT OR IGNORE INTO urls (url) VALUES (?)', (item['url'],))
        self.conn.commit()

        url_id = self.cursor.lastrowid

        # Perform NLP on body text to extract keywords
        doc = self.nlp(item['body_text'])
        keywords = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
        keyword_counts = Counter(keywords)

        # Store keywords in the database
        for keyword, freq in keyword_counts.items():
            self.cursor.execute('''INSERT INTO keywords (keyword, frequency, url_id) 
                                   VALUES (?, ?, ?)''', (keyword, freq, url_id))
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.conn.close()