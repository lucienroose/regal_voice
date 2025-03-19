#app.py
from flask import Flask, request, jsonify
import requests
import re
from dotenv import load_dotenv
import os
app = Flask(__name__)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def get_city_from_area_code(area_code):    
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
        "max_tokens": 10  # only return city
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        try:
            city = response.json()["choices"][0]["message"]["content"].strip()
            return city  
        except (KeyError, IndexError):
            pass

    return "Unknown City"  # Fallback if Mistral fails

def get_weather(city): #Fetch weather data by  city.
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},US&appid={WEATHER_API_KEY}&units=imperial"
    response = requests.get(url)
    
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
    data = request.get_json()
    from_number = data["call"].get("from_number", "")
    
    city = get_city_from_area_code(from_number)  
    weather_data = get_weather(city)
    
    if weather_data:
        return jsonify({
            "city": city,
            "temperature": weather_data["temperature"],
            "condition": weather_data["condition"]
        }), 200, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        return jsonify({"city": city, "temperature": None, "condition": "Weather data unavailable"}), 200
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
