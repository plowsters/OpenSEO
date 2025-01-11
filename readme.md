# Getting Started
This project is currently a WIP. These features are still to be implemented:

- Config File
- Control over which articles (and how many) are crawled by scrapy
- Misconfigured scrapy_selenium driver (need to put in docker container so driver doesn't interfere with my personal web browser)
- SQLite DB connection to store article content
- NLP analysis of article content for SEO suggestions
- SEO score algorithm
- Autogen Agents chat w/ interchangeable LLM (locally run or API access)
- Integration with Google Trends for Keyword Trend Analysis

What currently works:

- scrapy successfully scrapes articles on Medium and Substack under the tags 'AI' and 'Machine Learning'
- scrapy collects URL, title, meta description, source, headers, keywords, and keyword frequency from scraped articles (does not successfully commit them to DB)
- basic tkinter GUI

## Step 1:
Create and source a python venv
```
python3 -m venv venv
source venv/bin/activate
```

## Step 2:
Install required packages:
`pip install -r requirements.txt`

## Step 3:
Run the program:
`python main.py`