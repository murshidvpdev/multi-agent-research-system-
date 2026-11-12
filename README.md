# Multi-Agent Research System

Give it a topic, and a small team of AI agents researches it for you. One searches the web, one reads the best source, one writes a report, and one critiques that report and gives it a score.

I built this to learn how multi-agent systems actually work: how agents use tools, how they hand work to each other, and how plain LLM chains differ from agents that make their own decisions.

## How it works

```
your topic
   │
   ▼
🔎 Search agent    searches the web with Tavily and picks the best sources
   │
   ▼
📄 Reader agent    opens the most relevant page and pulls out the key facts
   │
   ▼
✍️ Writer          turns those findings into a structured report
   │
   ▼
🧐 Critic          reviews the report, scores it out of 10, and suggests fixes
```

The first two are **agents**. They have tools (web search and a page scraper) and decide for themselves when and how to use them. The last two are **chains**: a fixed prompt goes to the model, and text comes back. Mixing both kinds was half the point of the project.

Everything runs on Groq (`openai/gpt-oss-120b`), so it's fast. A full run usually takes under a minute.

## Getting started

You'll need Python 3.12 and two free API keys:

- **Groq** for the LLM: [console.groq.com](https://console.groq.com)
- **Tavily** for web search: [tavily.com](https://tavily.com)

**1. Clone the repo and install dependencies**

```bash
git clone https://github.com/murshidvpdev/multi-agent-research-system-.git
cd multi-agent-research-system-

# with uv (recommended)
uv sync

# or with pip
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**2. Add your keys.** Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
```

**3. Run it**

```bash
streamlit run app.py
```

This opens the web app in your browser. Type a topic (or click one of the examples) and watch each agent do its part. When it's done, you'll get the report, the critic's score and feedback, and the raw research data behind it all. You can also download the report as a Markdown file.

Prefer the terminal? Edit the topic in `main.py` and run:

```bash
python main.py
```

## Project structure

```
├── app.py                  # Streamlit web app
├── main.py                 # run the pipeline from the terminal
└── src/
    ├── tools/tools.py      # the web search and scraper tools
    ├── agents/agents.py    # the LLM, the two agents, and the writer/critic chains
    └── pipeline/pipeline.py  # wires the four steps together
```

If you want to understand the code, read `pipeline.py` first. It's short and shows the whole flow in one place.

## Built with

[LangChain](https://python.langchain.com) · [Groq](https://groq.com) · [Tavily](https://tavily.com) · [Streamlit](https://streamlit.io) · trafilatura and readability for clean page extraction

## Known limitations

- The reader agent only reads **one** page in depth. The rest of the report relies on search snippets.
- Scraped pages are trimmed to about 6,000 characters to stay inside Groq's token limits.
- Some sites block scrapers. When that happens, the agent is told to try another URL.
- The critic grades the report, but its feedback isn't fed back to the writer yet. A rewrite loop based on the critique is next on my list.

Ideas and pull requests are welcome.
