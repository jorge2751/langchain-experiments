import os
from dotenv import find_dotenv, load_dotenv
from serpapi import GoogleSearch
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain


class SnapshotBot:

    load_dotenv(find_dotenv())

    def __init__(self):
        pass

    # Filter organic results
    def filter_organic_results(organic_results):
        filtered_results = []

        for result in organic_results:
            filtered_result = {
                'title': result.get('title'),
                'link': result.get('link'),
                # 'description': result.get('about_this_result', {}).get('source', {}).get('description')
            }
            filtered_results.append(filtered_result)

        return filtered_results

    def get_search_results(niche, location):

        params = {
            "engine": "google",
            "q": niche,
            "location": location,
            "api_key": os.getenv("SERPAPI_API_KEY")
        }

        # Get search results and pull out map pack and organic results
        search = GoogleSearch(params)
        results = search.get_dict()
        map_pack = results.get("local_results")
        organic_results = results.get("organic_results")
        
        return map_pack, organic_results

    def get_map_pack_analysis(map_pack, city):

        chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1)

        prompt = PromptTemplate(
            input_variables=["map_pack", "city"],
            template="""
            Here's the data you will analyze: {map_pack}

            Identify places results with the city name ({city}) in the title, more than 10 reviews, and connected websites.
            
            If there are more than 3 instances (e.g. 2 places with the city name in the title and 2 places with connected websites), say "Competition is too high", else say "Competition is low".

            Base your response on the provided data, and if insufficient, say "I don't know".
            
            Example response:
            "There are 3 places with the city name in the title, 2 places with more than 10 reviews, and 1 place with a connected website. Competition is too high."
            """,
        )

        chain = LLMChain(llm=chat, prompt=prompt)

        response = chain.run(map_pack=map_pack, city=city)
        return response

    def get_organic_analysis(organic_results, city):

        chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1)

        prompt = PromptTemplate(
            input_variables=["organic_results", "city"],
            template="""
            Analyze each object of this array of results: {organic_results}

            Count how many instances there are with the city name ({city}) in their title and how many instances there are witht the city name in their link.
            
            If there are more than 5 instances (e.g. 3 results with the city name in the website title and 3 results with the city name in their domain), say "Competition is too high", else say "Competition is low".

            Base your response on the provided data.
            
            Example response:
            "There are 3 results with the city name in the title and 1 with the city name in the link. Competition is low."
            """,
        )

        chain = LLMChain(llm=chat, prompt=prompt)

        response = chain.run(organic_results=organic_results, city=city)
        return response
