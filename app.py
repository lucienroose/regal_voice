#app.py
from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)
WEATHER_API_KEY = "f381e68eb9e65d0b8390f7257285831f"
MISTRAL_API_KEY = "MEardDjM1BcIahdzw6dX87ePPhBkNWnD"

def get_city_from_area_code(area_code):
    """Uses Mistral LLM to determine the most likely city based on area code."""
    
    prompt = f"What is the associated city for the area code {area_code} in the United States? Absolutely do not provide any extra words orexplanation. Only output the name of the city."

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistral-tiny",
        "messages": [
            {"role": "system", "content": "You are an expert in US area codes."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 10  # Keep response concise
    }

    response = requests.post(url, json=data, headers=headers)

    print("🤖 Mistral API Response Status:", response.status_code)  # Debugging
    print("📍 Mistral API Response:", response.text)  # Debugging

    if response.status_code == 200:
        try:
            city = response.json()["choices"][0]["message"]["content"].strip()
            return city  # ✅ Returns extracted city
        except (KeyError, IndexError):
            pass

    return "Unknown City"  # Fallback if Mistral fails

def get_weather(city):
    """Fetches real-time weather data for the city."""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},US&appid={WEATHER_API_KEY}&units=imperial"
    response = requests.get(url)
    
    print("🌦️ OpenWeatherMap API Response Status:", response.status_code)  # Debugging
    print("🌎 OpenWeatherMap API Response:", response.text)  # Debugging

    if response.status_code != 200:
        return None
    
    data = response.json()
    
    if "main" in data:
        temp = data["main"]["temp"]
        condition = data["weather"][0]["description"]
        return {"temperature": temp, "condition": condition}
    
    return None

@app.route('/get_weather', methods=['POST'])
def handle_request():
    """Handles incoming weather requests dynamically using Telnyx API."""
    data = request.get_json()
    from_number = data["call"].get("from_number", "")
    
    city = get_city_from_area_code(from_number)  # 🔄 Fetch city dynamically
    weather_data = get_weather(city)
    
    if weather_data:
        return jsonify(weather_data), 200, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        return jsonify({"temperature": None, "condition": "Weather data unavailable"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

""""
WEATHER_API_KEY = "f381e68eb9e65d0b8390f7257285831f"
NUMVERIFY_API_KEY = "7930b26af8b9f99dc3b4dc8210c59765"

def get_city_from_area_code(phone_number):
    Uses Numverify API to get the city from a phone number.
    url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={phone_number}"
    response = requests.get(url)
    
    print("📞 Numverify API Response Status:", response.status_code, flush=True)  # Debugging
    print("📍 Numverify API Response:", response.text, flush=True)

    if response.status_code == 200:
        data = response.json()
        if data.get("valid") and "location" in data:
            return data["location"]  # ✅ Returns city name
    return "Unknown City"  # Fallback if no match

def get_weather(city):
    Fetches real-time weather data for the city.
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},US&appid={WEATHER_API_KEY}&units=imperial"
    response = requests.get(url)
    
    print("🌦️ OpenWeatherMap API Response Status:", response.status_code, flush=True)  # Debugging
    print("🌎 OpenWeatherMap API Response:", response.text, flush=True)  # Debugging

    if response.status_code != 200:
        return None
    
    data = response.json()
    
    if "main" in data:
        temp = data["main"]["temp"]
        condition = data["weather"][0]["description"]
        return {"temperature": temp, "condition": condition}
    
    return None

@app.route('/get_weather', methods=['POST'])
def handle_request():
    Handles incoming weather requests dynamically using Numverify API.
    data = request.get_json()
    from_number = data["call"].get("from_number", "")
    print(from_number)

    city = get_city_from_area_code(from_number)  # 🔄 Uses API instead of dictionary
    
    weather_data = get_weather(city)
    
    if weather_data:
        return jsonify(weather_data), 200, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        return jsonify({"temperature": None, "condition": "Weather data unavailable"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
"""

"""
app = Flask(__name__)

# OpenWeatherMap API Key
WEATHER_API_KEY = "f381e68eb9e65d0b8390f7257285831f"

# Area Code to City Mapping
AREA_CODE_TO_CITY = {
    "716": "Buffalo",
    "303": "Denver",
    "212": "New York",
    "305": "Miami",
    "312": "Chicago"
}

def extract_area_code(phone_number):
 
    match = re.match(r"^\+1(\d{3})\d{7}$", phone_number)
    return match.group(1) if match else None

def get_weather(city):
   
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},US&appid={WEATHER_API_KEY}&units=imperial"
    response = requests.get(url)
    
    print("API Response Status:", response.status_code)  # Debugging step
    print("API Response Body:", response.text)  # Debugging step


    data = response.json() 
    if "main" in data:
        temp = data["main"]["temp"]
        condition = data["weather"][0]["description"]
        return f"{temp}°F with {condition}"  
    
    return "weather data unavailable"

@app.route('/get_weather', methods=['POST'])
def handle_request():
    data = request.get_json()
    
    # Extract phone number from request
    from_number = data.get("call", {}).get("from_number", "")
    area_code = extract_area_code(from_number)
    
    city = AREA_CODE_TO_CITY.get(area_code, "Unknown City")
    
    # Get weather data
    weather_info = get_weather(city)
    # Construct the response
    greeting = f"Hi! I see you're from {city}. Right now, it's {weather_info}. Hope you're having a great day! How can I assist you?"
    
    # ✅ Fix: Use `ensure_ascii=False` so UTF-8 characters (like °) are preserved
    return jsonify({"weather_info": greeting}), 200, {'Content-Type': 'application/json; charset=utf-8'}

    if area_code and area_code in AREA_CODE_TO_CITY:
        city = AREA_CODE_TO_CITY[area_code]
        weather_info = get_weather(city)
        greeting = f"Hi! I see you're from {city}. Right now, it's {weather_info}. Hope you're having a great day! How can I assist you?"
    else:
        greeting = "Hi! Welcome to Lemonade. How can I assist you today?"
    
    return jsonify({"weather_info": greeting})
  
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
"""