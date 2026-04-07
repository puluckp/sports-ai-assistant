# agent.py

import json
from openai import OpenAI
from tools import tools

from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))



def get_response(user_message, previous_response_id=None):
    params = {}
    if previous_response_id:
        params["previous_response_id"] = previous_response_id

    response = client.responses.create(
        model="gpt-4o-mini",
        input=user_message,
        instructions="You are a sports assistant which summarises sports news. When responding ensure to follow the following format: [Event detail; Scores details; biggest highlight of the match.]. Don't explicitly call out these headings in the response though just use new paragraphs for each. All text under these headers should be in max 2-3 lines. Don't answer any non-sports related queries.",
        tools=tools,
        **params
    )
    #print(response.output)
    
    return response.output[-1].content[0].text, response.id
