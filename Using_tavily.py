import os
import json
import tavily
from datetime import datetime
from langchain_ollama import ChatOllama

# ---------------------------------------
# 1) Initialize Tavily Client
# ---------------------------------------
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
# Direct test key (temporary)
TAVILY_API_KEY = "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"

if not TAVILY_API_KEY:
    raise ValueError(" API Key for Tavily is missing. Set it in Environment Variable TAVILY_API_KEY.")

client = tavily.TavilyClient(api_key=TAVILY_API_KEY)

# ---------------------------------------
# 2) Initialize Ollama LLM
# ---------------------------------------
llm = ChatOllama(
    model="OxW/Qwen3-0.6B-GGUF",
    temperature=0,
    format="json"
)

# ---------------------------------------
# 3) Tavily Search Function
# ---------------------------------------
def tavily_search(query, max_results=3):
    results = client.search(query=query, num_results=max_results)
    combined_text = "\n".join(results)
    return combined_text

# ---------------------------------------
# 4) Function to Get Country Information
# ---------------------------------------
def get_country_info(country_name):
    search_results = tavily_search(f"Recent information about the country {country_name}")
    
    prompt = f"""
    You have the following search results about the country "{country_name}":
    {search_results}

    Using ONLY the information from the search results, generate a complete JSON with the following structure:
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

    Return ONLY the JSON with no additional text.
    """
    
    response = llm.invoke(prompt)
    
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        print(" ERROR: LLM could not return valid JSON. Please try again.")
        return {}

# ---------------------------------------
# 5) User Input + Save JSON to RESULTS Folder
# ---------------------------------------
if __name__ == "__main__":
    country_name = input("Enter country name: ").strip()
    if not country_name:
        print("Please enter a valid country name.")
        exit()

    info = get_country_info(country_name)

    if info:
        # Print result on screen
        print(json.dumps(info, indent=2, ensure_ascii=False))

        # Create RESULTS folder if not exists
        results_folder = "RESULTS"
        os.makedirs(results_folder, exist_ok=True)

        # File name: country + date
        today = datetime.now().strftime("%Y-%m-%d")
        file_name = f"{country_name}_{today}.json"
        file_path = os.path.join(results_folder, file_name)

        # Save the file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

        print(f" DONE: {file_path}")
    else:
        print(" NOT VALID.")
