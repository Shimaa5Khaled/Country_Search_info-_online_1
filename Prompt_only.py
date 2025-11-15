# A) Loading model 
import json
import requests
# from langchain_community.chat_models import ChatOllama
from langchain_ollama import ChatOllama


llm = ChatOllama(model="OxW/Qwen3-0.6B-GGUF", format="json", temperature=0)

def get_country_info_from_llm(country_name):
    prompt = f"""
You are a country-information assistant.
If I give you a country name: "{country_name}",
return the information in JSON format like this:
    {{
  "President Name": "",
  "capital": "",
  "continent": "",
  "population": "",
  "language": "",
  "currency": "",
  "government_type": "",
  "timezone": "",
  "weather": {{
    "average_temperature": "",
    "climate": ""
  }},
  "major_cities": [],
  "famous_landmarks": [],
  "economy": {{
    "main_sectors": [],
    "gdp": ""
  }},
  "tourism": {{
    "popular_destinations": [],
    "best_time_to_visit": ""
  }},
  "flag_colors": [],
  "neighbors": []
}}
"""
    answer = llm.invoke(prompt)
    return json.loads(answer.content)

country_name = input("Enter the country name: ")

# Call the function
result = get_country_info_from_llm(country_name)

# Print the result
print(result)



