from langchain_google_genai import ChatGoogleGenerativeAI


import os
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults
wrapper = DuckDuckGoSearchAPIWrapper(region="de-de", time="d", max_results=2)

search = DuckDuckGoSearchResults(api_wrapper=wrapper, source="news")

a = search.invoke("market prize of steel")
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro", api_key=os.getenv("GROQ_API_KEY"))


aa = llm.invoke(
    f"Just return the current price from the given text nothing else only the current price {a}")
print(aa.content)
