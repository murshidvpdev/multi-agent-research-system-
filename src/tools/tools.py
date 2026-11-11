from langchain.tools import tool
import requests
from dotenv import load_dotenv
import os
from tavily import TavilyClient
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re

load_dotenv()


tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def tavily_search(query: str) -> str:
    """
    Search the web using Tavily API and return the results.
    """
    try:
        results = tavily.search(query, max_results=5)
        out = []
        for result in results['results']:
            out.append(f"Title: {result['title']}\nURL: {result['url']}\nSnippet: {result['raw_content']}\n")
        return "\n".join(out)
    except Exception as e:
        return f"An error occurred while searching: {str(e)}"


@tool
def scrape_webpage(url: str) -> str:
    """
    Scrape the content of a webpage and return the text.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text

        # Use readability to extract the main content
        doc = Document(html_content)
        main_content = doc.summary()

        # Use BeautifulSoup to clean up the HTML
        soup = BeautifulSoup(main_content, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)

        # Optionally, use trafilatura for better extraction
        trafilatura_text = trafilatura.extract(html_content)
        if trafilatura_text:
            text += "\n\n" + trafilatura_text

        return text
    except Exception as e:
        return f"An error occurred while scraping the webpage: {str(e)}"