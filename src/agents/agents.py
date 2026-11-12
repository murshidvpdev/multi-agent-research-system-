from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import tavily_search, scrape_webpage
from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
    )

# first agent that can search the web using Tavily API
def build_search_agent():
    tools = [tavily_search]
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are a web research assistant. Use the tavily_search tool to find "
            "recent, reliable sources on the user's topic. Return a concise list of "
            "the best results, each with its title, URL and a one-line summary."
        ),
    )
    return agent

# second agent that can scrape webpages
def build_scraper_agent():
    tools = [scrape_webpage]
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are a content extraction assistant. Use the scrape_webpage tool on "
            "the most relevant URL you are given (try another if it fails). Return "
            "the key facts, figures and insights from the page, plus the source URL."
        ),
    )
    return agent


# writen chain

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert researcher that writes content based on the given input. strcutured and insightful. Provide a well-organized and comprehensive response to the user's query. Use clear headings, bullet points, and examples where appropriate. Ensure that the content is accurate, relevant, and easy to understand. Avoid unnecessary jargon and keep the language concise and engaging."),
    ("human", """
    write a detailed and well-structured article based on the following input. Ensure that the content is informative, engaging, and easy to understand. Use clear headings, bullet points, and examples where appropriate. Avoid unnecessary jargon and keep the language concise and accessible
    topic :{topic}
    Research findings : {research_findings}

    structure the resport as:
        - Introduction: Provide an overview of the topic and its significance.
        - Key Findings: Summarize the main research findings and insights.
        - Conclusion: Offer a concise summary of the key points and implications of the research.
        - Sources: List the sources used for the research, including any relevant links or references.

    Be Detailed and comprehensive in your response, ensuring that all relevant information is included. Use clear and concise language, and organize the content in a logical and coherent manner.
    
    
    """)
])
writen_chain = writer_prompt | llm | StrOutputParser()

# critic prompt

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an sharp and constructive research critic that provides insightful feedback on research findings. Your role is to evaluate the quality, relevance, and significance of the research, and to offer suggestions for improvement. Be thorough, objective, and constructive in your feedback.,Be honest and specific in your critique, and provide actionable recommendations for enhancing the research. Use clear and concise language, and organize your feedback in a logical and coherent manner."),
    ("human", """
    Review the research findings provided and offer a detailed critique of the work. Your feedback should be constructive, highlighting both strengths and areas for improvement. Consider the following aspects in your critique:
    Report:
    {report}
    Respond in this exact format:
    Score: [Provide a numerical score out of 10, with 10 being the highest possible score.]
    Strengths: [Highlight the key strengths of the research, including any innovative approaches, significant findings, or well-supported arguments.]
    Weaknesses: [Identify any weaknesses or limitations in the research, such as gaps in the literature, methodological issues, or areas where the analysis could be improved.]
    Suggestions for Improvement: [Offer specific recommendations for enhancing the research, including potential avenues for further investigation, alternative methodologies, or additional sources that could strengthen the work.]
    """)])


critic_chain = critic_prompt | llm | StrOutputParser()

