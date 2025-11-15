from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
from datetime import datetime
import tavily
from langchain_ollama import ChatOllama


app = FastAPI()

# ---------------------------------------
# Tavily API Key
# ---------------------------------------
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise ValueError(" API Key for Tavily is missing. Set it in Environment Variable TAVILY_API_KEY.")

client = tavily.TavilyClient(api_key=TAVILY_API_KEY)

llm = ChatOllama(
    model="OxW/Qwen3-0.6B-GGUF",
    temperature=0,
    format="json"
)


def tavily_search(query, max_results=3):
    results = client.search(query=query, num_results=max_results)
    
    if isinstance(results, list):
        combined_text = "\n".join([str(r) for r in results])
    else:
        combined_text = str(results)
    return combined_text


def get_country_info(country_name: str):
    search_results = tavily_search(f"Recent information about the country {country_name}")
    
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

Return JSON only without any text outside the JSON.
    """
    
    response = llm.invoke(prompt)
    
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return {}


class CountryRequest(BaseModel):
    country_name: str

@app.post("/")
def fetch_country_info(request: CountryRequest):
    country_name = request.country_name.strip()
    if not country_name:
        raise HTTPException(status_code=400, detail="Country name is required.")

    info = get_country_info(country_name)
    if not info:
        raise HTTPException(status_code=500, detail="Valid data was not received from the LLM.")

    # Save result into RESULTS folder
    results_folder = "RESULTS"
    os.makedirs(results_folder, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    file_name = f"{country_name}_{today}.json"
    file_path = os.path.join(results_folder, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    return {
        "message": "Data retrieved and saved successfully",
        "file_path": file_path,
        "data": info
    }

@app.get("/get_country_info/{country_name}")
def fetch_country_info_get(country_name: str):
    return fetch_country_info(CountryRequest(country_name=country_name))
