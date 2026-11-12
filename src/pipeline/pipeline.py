from src.agents.agents import build_search_agent, build_scraper_agent, writen_chain, critic_chain


def _final_text(agent_result):
    """An agent returns {"messages": [...]}; the last message is its final answer."""
    return agent_result["messages"][-1].content


def run_research_system(query, on_step=None):
    """
    Run the 4-step research pipeline and return a state dict with every step's output.

    on_step(step, data) is optional: it is called after each step finishes so a UI
    can show live progress. step is one of "search", "scrape", "report", "critique".
    """
    def notify(step, data):
        if on_step:
            on_step(step, data)

    state = {}

    # Step 1: search agent finds relevant pages (agents take chat messages as input)
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable info about: {query}")]
    })
    state["search_results"] = _final_text(search_result)
    notify("search", state["search_results"])

    # Step 2: scraper agent picks the best URL from the search results and reads it
    scraper_agent = build_scraper_agent()
    scrape_result = scraper_agent.invoke({
        "messages": [("user",
            f"Topic: {query}\n\n"
            f"Search results:\n{state['search_results']}\n\n"
            "Pick the most relevant URL, scrape it, and return the key findings."
        )]
    })
    state["scraped_content"] = _final_text(scrape_result)
    notify("scrape", state["scraped_content"])

    # Step 3: writer chain turns the findings into a structured report
    # (search results are included too, so the report can cite all sources)
    state["report"] = writen_chain.invoke({
        "topic": query,
        "research_findings": f"{state['scraped_content']}\n\nOther search results:\n{state['search_results']}"
    })
    notify("report", state["report"])

    # Step 4: critic chain reviews the report
    state["critique"] = critic_chain.invoke({"report": state["report"]})
    notify("critique", state["critique"])

    return state
