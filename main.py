from src.tools.tools import tavily_search,scrape_webpage
from rich import print

web_scrape = scrape_webpage.invoke({"url": "https://aiweekly.co/"})
taviley_results = tavily_search.invoke({"query": "AI Weekly"})

print(web_scrape)
print(taviley_results)