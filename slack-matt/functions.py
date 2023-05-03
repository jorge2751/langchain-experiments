from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
from dotenv import find_dotenv, load_dotenv
from serpapi import GoogleSearch
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import os

load_dotenv(find_dotenv())

def get_search_results(niche, location):

    params = {
        "engine": "google",
        "q": niche,
        "location": location,
        "api_key": os.getenv("SERPAPI_API_KEY"),
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    map_pack = results.get("local_results")
    return map_pack

def get_response_from_query(search_results, city):
    
    chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1)
    
    prompt = PromptTemplate(
        input_variables=["search_results", "city"],
        template="""
        Here's the data you will analyze: {search_results}

        Identify places results with the city name ({city}) in the title, more than 10 reviews, and connected websites.
        
        If there are more than 3 instances (e.g. 2 places with the city name in the title and 2 places with connected websites), say "Competition is too high", else say "Competition is low".

        Base your response on the provided data, and if insufficient, say "I don't know".
        
        Example response:
        "There are 3 places with the city name in the title, 2 places with more than 10 reviews, and 1 place with a connected website. Competition is too high."
        """,
    )

    chain = LLMChain(llm=chat, prompt=prompt)

    response = chain.run(search_results=search_results, city=city)
    return response