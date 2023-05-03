from langchain.llms import OpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
from dotenv import find_dotenv, load_dotenv
from google_places_api_wrapper import GooglePlacesAPIWrapper
import textwrap

load_dotenv(find_dotenv())

def get_search_results(location: str, niche: str) -> str:
    search = GooglePlacesAPIWrapper()
    query = f"{niche} businesses in {location}"
    search_results = search.run(query)

    return search_results

def get_response_from_query(search_results, query):
    llm = OpenAI(model_name="text-davinci-003")

    prompt = PromptTemplate(
        input_variables=["question", "search_results"],
        template="""
        You are a helpful assistant that can analyze businesses based on the information
        available in Google Maps search results.

        Answer the following question: {question}
        By searching the following businesses' information: {search_results}

        Only use the factual information from the search results to answer the question.

        If you feel like you don't have enough information to answer the question, say "I don't know".

        Your answers should be verbose and detailed.
        """,
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    response = chain.run(question=query, search_results=search_results)
    response = response.replace("\n", "")
    return response

# Example usage:
location = "New York City"
niche = "coffee shops"
search_results = get_search_results(location, niche)

query = "What can you tell me about the top coffee shops in New York City?"
response = get_response_from_query(search_results, query)
print(textwrap.fill(response, width=85))
