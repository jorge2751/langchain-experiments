import os
from dotenv import find_dotenv, load_dotenv
from langchain.agents import load_tools, initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain import PromptTemplate
from serpapi import GoogleSearch

class SnapshotBot:
    
    load_dotenv(find_dotenv())
    slack_bot_token = os.environ["SNAPSHOT_BOT_TOKEN"]
    slack_signing_secret = os.environ["SNAPSHOT_SIGNING_SECRET"]
    slack_bot_user_id = os.environ["SNAPSHOT_BOT_USER_ID"]
    llm =ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1)
    
    def __init__(self):
        self.tools = load_tools(["serpapi", "llm-math"], llm=self.llm)
        self.agent = initialize_agent(self.tools, self.llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    
    @classmethod
    def process_message(cls, message):
        text = message["event"]["text"]
        mention = f"<@{cls.slack_bot_user_id}>"
        
        # Remove the mention from the text
        text = text.replace(mention, "").strip()
        
        # Extract niche, city, and state from the user input
        try:
            niche, city, state = [x.strip() for x in text.split(",")]
        except ValueError:
            return "Please provide the input in the format 'niche, city, state'"

        return niche, city, state
    
    @classmethod
    def get_search_results(cls, niche, location):
        
        params = {
            "engine": "google",
            "q": niche,
            "location": location,
            "api_key": os.getenv("SERPAPI_API_KEY")
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        map_pack = results.get("local_results")
        return map_pack
    
    @classmethod
    def get_response_from_query(cls, search_results, city):
        
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

        chain = LLMChain(llm=cls.llm, prompt=prompt)

        response = chain.run(search_results=search_results, city=city)
        return response