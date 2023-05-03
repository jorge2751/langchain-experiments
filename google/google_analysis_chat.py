from langchain.llms import OpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
from dotenv import find_dotenv, load_dotenv
from serpapi import GoogleSearch
import os
import textwrap

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
    print(map_pack)
    return map_pack


def get_response_from_query(search_results, city):
    llm = OpenAI(model_name="text-davinci-003")

    prompt = PromptTemplate(
        input_variables=["search_results", "city"],
        template="""
        As a helpful assistant analyzing Google Maps search results, analyze the requested paramaters for this data: {search_results}.

        Identify places results with the city name ({city}) in the title, more than 10 reviews, and connected websites.
        
        If there are more than 3 instances (e.g. 2 places with the city name in the title and 2 places with connected websites), say "Competition is too high", else say "Competition is low".

        Base your response on the provided data, and if insufficient, say "I don't know".
        
        Example response:
        "There are 3 places with the city name in the title, 2 places with more than 10 reviews, and 1 place with a connected website. Competition is too high."
        """,
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    response = chain.run(search_results=search_results, city=city)
    return response


# Example usage:
# city = "Ventura"
# state = "California"
# location = f"{city}, {state}"
# niche = "roofing"

# search_results = get_search_results(niche, location)

# response = get_response_from_query(search_results, city)
# print(textwrap.fill(response, width=50))
