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

# ---------------------------
def get_population(country_name):
    url = f"https://restcountries.com/v3.1/name/{country_name}"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()[0]
        pop = data.get("population", "Unknown")
        return f"{pop:,} people"
    return "Unknown "

def get_currency(country_name):
    url = f"https://restcountries.com/v3.1/name/{country_name}"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()[0]
        currencies = data.get("currencies", {})
        if currencies:
            code = list(currencies.keys())[0]
            name = currencies[code].get("name", "")
            return f"{name} ({code})"
    return "Unknown "

def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=j1"
        res = requests.get(url)
        data = res.json()
        temp = data['current_condition'][0]['temp_C']
        climate = data['current_condition'][0]['weatherDesc'][0]['value']
        return {
            "average_temperature": f"{temp}°C",
            "climate": climate
        }
    except:
        return {"average_temperature":"Unknown ", "climate": "Unknown"}


def main():
    country_name = input("input country name: ")
    
    info = get_country_info_from_llm(country_name)
    
    info['population'] = get_population(country_name)
    info['currency'] = get_currency(country_name)
    info['weather'] = get_weather(info.get('capital', country_name))
    
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
