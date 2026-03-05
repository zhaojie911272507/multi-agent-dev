import os
from pprint import pprint

from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

client = OpenAI(
    base_url="https://api.subconscious.dev/v1",
    api_key=os.getenv("SUBCONSCIOUS_API_KEY"),
)

response = client.chat.completions.create(
    model="tim-small-preview",
    messages=[
        {"role": "user", "content": "今天是农历几号？"}
    ],
    tools=[
        { "type": "web_search" }
    ],
)

pprint(response.choices[0].message.content)

