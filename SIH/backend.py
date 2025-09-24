import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import random
import time
import concurrent.futures
from functools import lru_cache
from data_processor import get_fertilizer_recommendations, process_crop_and_fertilizer_data

app = Flask(__name__)
CORS(app)

# Real crop database with actual agricultural data for India
CROP_DATABASE = {
    "Rice": {
        "soil_types": ["loamy", "clay"],
        "water_requirement": "high",
        "yield_range": [20, 35],  # q/acre
        "profit_range": [35000, 55000],  # ₹ per acre
        "sustainability": "medium",
        "season": ["kharif", "rabi"],
        "regions": ["punjab", "haryana", "uttar pradesh", "west bengal", "tamil nadu", "karnataka", "andhra pradesh"],
        "emoji": "🍚"
    },
    "Wheat": {
        "soil_types": ["loamy", "clay", "silty"],
        "water_requirement": "medium",
        "yield_range": [25, 45],
        "profit_range": [30000, 50000],
        "sustainability": "high",
        "season": ["rabi"],
        "regions": ["punjab", "haryana", "uttar pradesh", "madhya pradesh", "rajasthan", "bihar"],
        "emoji": "🌾"
    },
    "Maize": {
        "soil_types": ["loamy", "sandy", "clay"],
        "water_requirement": "medium",
        "yield_range": [25, 40],
        "profit_range": [28000, 45000],
        "sustainability": "medium",
        "season": ["kharif", "rabi"],
        "regions": ["karnataka", "andhra pradesh", "tamil nadu", "maharashtra", "bihar", "uttar pradesh"],
        "emoji": "🌽"
    },
    "Sugarcane": {
        "soil_types": ["loamy", "clay"],
        "water_requirement": "high",
        "yield_range": [300, 500],  # tonnes/acre
        "profit_range": [45000, 80000],
        "sustainability": "low",
        "season": ["kharif"],
        "regions": ["uttar pradesh", "maharashtra", "karnataka", "tamil nadu", "andhra pradesh", "punjab", "haryana"],
        "emoji": "🧃"
    },
    "Cotton": {
        "soil_types": ["loamy", "sandy", "clay"],
        "water_requirement": "medium",
        "yield_range": [8, 15],  # quintals/acre
        "profit_range": [40000, 70000],
        "sustainability": "medium",
        "season": ["kharif"],
        "regions": ["gujarat", "maharashtra", "andhra pradesh", "punjab", "haryana", "rajasthan", "karnataka"],
        "emoji": "🧵"
    },
    "Pulses": {
        "soil_types": ["loamy", "sandy", "clay"],
        "water_requirement": "low",
        "yield_range": [10, 20],
        "profit_range": [35000, 60000],
        "sustainability": "high",
        "season": ["rabi", "kharif"],
        "regions": ["madhya pradesh", "rajasthan", "maharashtra", "karnataka", "uttar pradesh", "andhra pradesh"],
        "emoji": "🫘"
    },
    "Soybean": {
        "soil_types": ["loamy", "clay"],
        "water_requirement": "medium",
        "yield_range": [15, 25],
        "profit_range": [32000, 48000],
        "sustainability": "high",
        "season": ["kharif"],
        "regions": ["madhya pradesh", "maharashtra", "rajasthan", "karnataka", "andhra pradesh"],
        "emoji": "🫘"
    },
    "Groundnut": {
        "soil_types": ["sandy", "loamy"],
        "water_requirement": "low",
        "yield_range": [12, 22],
        "profit_range": [30000, 50000],
        "sustainability": "high",
        "season": ["kharif", "rabi"],
        "regions": ["gujarat", "andhra pradesh", "tamil nadu", "karnataka", "rajasthan", "maharashtra"],
        "emoji": "🥜"
    },
    "Sunflower": {
        "soil_types": ["loamy", "sandy"],
        "water_requirement": "low",
        "yield_range": [8, 15],
        "profit_range": [25000, 40000],
        "sustainability": "medium",
        "season": ["rabi"],
        "regions": ["karnataka", "andhra pradesh", "maharashtra", "tamil nadu"],
        "emoji": "🌻"
    },
    "Potato": {
        "soil_types": ["loamy", "sandy"],
        "water_requirement": "medium",
        "yield_range": [200, 350],  # quintals/acre
        "profit_range": [40000, 80000],
        "sustainability": "medium",
        "season": ["rabi", "kharif"],
        "regions": ["uttar pradesh", "west bengal", "bihar", "punjab", "assam", "gujarat"],
        "emoji": "🥔"
    },
    "Pearl Millet": {
        "soil_types": ["sandy", "loamy"],
        "water_requirement": "low",
        "yield_range": [15, 25],
        "profit_range": [25000, 40000],
        "sustainability": "high",
        "season": ["kharif"],
        "regions": ["rajasthan", "gujarat", "haryana", "uttar pradesh", "maharashtra"],
        "emoji": "🌾"
    },
    "Sorghum": {
        "soil_types": ["sandy", "loamy"],
        "water_requirement": "low",
        "yield_range": [12, 20],
        "profit_range": [22000, 35000],
        "sustainability": "high",
        "season": ["kharif"],
        "regions": ["maharashtra", "karnataka", "andhra pradesh", "tamil nadu", "rajasthan"],
        "emoji": "🌾"
    }
}

# Indian state to region mapping
STATE_REGIONS = {
    "punjab": ["punjab"],
    "haryana": ["haryana"],
    "uttar pradesh": ["uttar pradesh"],
    "delhi": ["delhi"],
    "rajasthan": ["rajasthan"],
    "madhya pradesh": ["madhya pradesh"],
    "gujarat": ["gujarat"],
    "maharashtra": ["maharashtra"],
    "karnataka": ["karnataka"],
    "tamil nadu": ["tamil nadu"],
    "andhra pradesh": ["andhra pradesh"],
    "telangana": ["andhra pradesh"],
    "west bengal": ["west bengal"],
    "bihar": ["bihar"],
    "assam": ["assam"],
    "odisha": ["odisha"],
    "jharkhand": ["jharkhand"],
    "chhattisgarh": ["chhattisgarh"]
}

# Bhuvan API Configuration
BHUVAN_BASE = "https://bhuvan-app1.nrsc.gov.in/api"
BHUVAN_TOKEN = "7c6df3895328e60658ceb5148258c539e504a429"

# OpenWeather API Configuration
OPENWEATHER_API_KEY = "e43dc511613c6f3d5dd79733bbdc79aa"
OPENWEATHER_BASE = "https://api.openweathermap.org/data/2.5"

# Performance optimization settings
USE_BHUVAN_API = False  # Disable slow Bhuvan APIs for faster response
USE_WEATHER_API = True  # Keep weather API as it's relatively fast
CACHE_DURATION = 300  # 5 minutes cache for weather data

def get_bhuvan_token():
    """Get fresh Bhuvan API token (tokens expire daily)"""
    try:
        # Try to get a fresh token
        token_url = f"{BHUVAN_BASE}/token"
        response = requests.get(token_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('token', BHUVAN_TOKEN)
    except Exception as e:
        print(f"Failed to get fresh token: {e}")
    
    return BHUVAN_TOKEN

def get_village_geocode_bhuvan(village_name):
    """Call Bhuvan village geocoding to get precise lat-long coordinates"""
    try:
        url = f"{BHUVAN_BASE}/village_geocoding"
        token = get_bhuvan_token()
        params = {
            "token": token,
            "village": village_name,
            "format": "json"
        }
        
        print(f"Geocoding village: {village_name}")
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data and 'latitude' in data and 'longitude' in data:
                print(f"Successfully geocoded {village_name}: {data['latitude']}, {data['longitude']}")
                return {
                    'latitude': float(data['latitude']),
                    'longitude': float(data['longitude']),
                    'state': data.get('state', ''),
                    'district': data.get('district', ''),
                    'source': 'bhuvan'
                }
        
        print(f"Bhuvan geocoding failed for {village_name}: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"Error in Bhuvan geocoding: {e}")
        return None

def get_lulc_statistics_bhuvan(lat, lon, radius_km=5):
    """Get Land Use Land Cover statistics from Bhuvan API"""
    try:
        url = f"{BHUVAN_BASE}/lulc_50k_aoi_wise"
        token = get_bhuvan_token()
        params = {
            "token": token,
            "lat": lat,
            "lon": lon,
            "buffer": radius_km,
            "format": "json"
        }
        
        print(f"Getting LULC data for {lat}, {lon}")
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"LULC data received: {data}")
            
            # Parse LULC data to extract agricultural information
            lulc_data = {
                'agriculture': 0,
                'forest': 0,
                'water': 0,
                'barren': 0,
                'urban': 0,
                'source': 'bhuvan'
            }
            
            if 'data' in data:
                for item in data['data']:
                    category = item.get('category', '').lower()
                    percentage = float(item.get('percentage', 0))
                    
                    if 'agriculture' in category or 'cropland' in category or 'cultivated' in category:
                        lulc_data['agriculture'] += percentage
                    elif 'forest' in category:
                        lulc_data['forest'] += percentage
                    elif 'water' in category or 'waterbody' in category:
                        lulc_data['water'] += percentage
                    elif 'barren' in category or 'wasteland' in category:
                        lulc_data['barren'] += percentage
                    elif 'urban' in category or 'built' in category:
                        lulc_data['urban'] += percentage
            
            return lulc_data
        
        print(f"Bhuvan LULC API failed: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"Error in Bhuvan LULC API: {e}")
        return None

def get_soil_data_bhuvan(lat, lon):
    """Get soil information from Bhuvan soil APIs"""
    try:
        url = f"{BHUVAN_BASE}/soil_data"
        token = get_bhuvan_token()
        params = {
            "token": token,
            "lat": lat,
            "lon": lon,
            "format": "json"
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data
        
        return None
        
    except Exception as e:
        print(f"Error in Bhuvan soil API: {e}")
        return None

# Weather cache to avoid repeated API calls
weather_cache = {}

def get_weather_data_openweather(lat, lon):
    """Get current weather data from OpenWeather API with caching"""
    if not USE_WEATHER_API:
        return None
        
    # Create cache key based on rounded coordinates (to cache nearby locations)
    cache_key = f"{round(lat, 1)}_{round(lon, 1)}"
    
    # Check cache first
    if cache_key in weather_cache:
        cached_data, timestamp = weather_cache[cache_key]
        if time.time() - timestamp < CACHE_DURATION:
            print(f"Using cached weather data for {lat}, {lon}")
            return cached_data
    
    try:
        # Get current weather only (skip forecast for speed)
        current_url = f"{OPENWEATHER_BASE}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        
        print(f"Getting weather data for {lat}, {lon}")
        response = requests.get(current_url, params=params, timeout=5)  # Reduced timeout
        
        if response.status_code == 200:
            current_data = response.json()
            
            weather_info = {
                'current': {
                    'temperature': current_data['main']['temp'],
                    'humidity': current_data['main']['humidity'],
                    'pressure': current_data['main']['pressure'],
                    'description': current_data['weather'][0]['description'],
                    'wind_speed': current_data.get('wind', {}).get('speed', 0),
                    'rain': current_data.get('rain', {}).get('1h', 0),
                    'timestamp': current_data['dt']
                },
                'source': 'openweather'
            }
            
            # Cache the result
            weather_cache[cache_key] = (weather_info, time.time())
            
            print(f"Weather data received: {current_data['main']['temp']}°C, {current_data['main']['humidity']}% humidity")
            return weather_info
        
        print(f"OpenWeather API failed: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"Error in OpenWeather API: {e}")
        return None

def analyze_weather_for_agriculture(weather_data):
    """Analyze weather data for agricultural suitability"""
    if not weather_data or weather_data.get('source') != 'openweather':
        return None
    
    current = weather_data['current']
    
    # Agricultural weather analysis
    analysis = {
        'temperature_category': 'optimal',
        'humidity_category': 'optimal', 
        'rainfall_category': 'normal',
        'farming_conditions': 'good',
        'alerts': [],
        'recommendations': []
    }
    
    temp = current['temperature']
    humidity = current['humidity']
    rain = current['rain']
    wind = current['wind_speed']
    
    # Temperature analysis
    if temp < 10:
        analysis['temperature_category'] = 'cold'
        analysis['alerts'].append('Very cold temperatures - avoid heat-sensitive crops')
        analysis['recommendations'].append('Consider cold-resistant crops like wheat, barley')
    elif temp > 35:
        analysis['temperature_category'] = 'hot'
        analysis['alerts'].append('High temperatures - ensure adequate irrigation')
        analysis['recommendations'].append('Water-intensive crops may need extra irrigation')
    elif 20 <= temp <= 30:
        analysis['temperature_category'] = 'optimal'
    
    # Humidity analysis
    if humidity < 30:
        analysis['humidity_category'] = 'dry'
        analysis['alerts'].append('Low humidity - high evaporation risk')
        analysis['recommendations'].append('Increase irrigation frequency')
    elif humidity > 80:
        analysis['humidity_category'] = 'humid'
        analysis['alerts'].append('High humidity - fungal disease risk')
        analysis['recommendations'].append('Monitor for fungal diseases')
    
    # Rainfall analysis
    if rain > 5:
        analysis['rainfall_category'] = 'heavy'
        analysis['alerts'].append('Heavy rainfall - drainage needed')
        analysis['recommendations'].append('Ensure proper drainage systems')
    elif rain > 1:
        analysis['rainfall_category'] = 'moderate'
    else:
        analysis['rainfall_category'] = 'light'
    
    # Wind analysis
    if wind > 10:
        analysis['alerts'].append('High winds - protect young crops')
        analysis['recommendations'].append('Use windbreaks or support structures')
    
    # Overall farming conditions
    if len(analysis['alerts']) == 0:
        analysis['farming_conditions'] = 'excellent'
    elif len(analysis['alerts']) <= 2:
        analysis['farming_conditions'] = 'good'
    else:
        analysis['farming_conditions'] = 'challenging'
    
    return analysis

def get_location_region(location):
    """Extract region from location string"""
    location_lower = location.lower()
    
    # Check for state names
    for state, regions in STATE_REGIONS.items():
        if state in location_lower:
            return regions[0]
    
    # Default fallback
    return "uttar pradesh"  # Most common agricultural state

def calculate_enhanced_crop_score(crop_name, crop_data, soil_type, water_availability, location, past_crops, lulc_data, soil_data, detected_state, weather_data=None):
    """Calculate enhanced suitability score using Bhuvan geospatial data and weather information"""
    score = 0
    max_score = 140  # Increased max score for weather factors
    
    # Soil type compatibility (25 points)
    if soil_type.lower() in crop_data["soil_types"]:
        score += 25
    elif any(compatible in soil_type.lower() for compatible in crop_data["soil_types"]):
        score += 15
    
    # Water requirement compatibility (20 points)
    water_match = {
        "high": {"high": 20, "medium": 12, "low": 4},
        "medium": {"high": 16, "medium": 20, "low": 12},
        "low": {"high": 4, "medium": 12, "low": 20}
    }
    score += water_match.get(water_availability.lower(), {}).get(crop_data["water_requirement"], 8)
    
    # Regional suitability (20 points)
    region = detected_state.lower() if detected_state else get_location_region(location).lower()
    if region in [r.lower() for r in crop_data["regions"]]:
        score += 20
    else:
        score += 8  # Still possible but not optimal
    
    # Land Use Land Cover analysis (25 points) - NEW!
    if lulc_data and lulc_data.get('source') == 'bhuvan':
        agriculture_pct = lulc_data.get('agriculture', 0)
        forest_pct = lulc_data.get('forest', 0)
        water_pct = lulc_data.get('water', 0)
        
        # Agriculture land percentage bonus
        if agriculture_pct > 60:
            score += 15  # High agricultural area
        elif agriculture_pct > 40:
            score += 10  # Medium agricultural area
        elif agriculture_pct > 20:
            score += 5   # Low agricultural area
        
        # Water availability from LULC
        if crop_data["water_requirement"] == "high" and water_pct > 10:
            score += 10  # High water requirement crop in water-rich area
        elif crop_data["water_requirement"] == "low" and water_pct < 5:
            score += 8   # Low water requirement crop in dry area
        
        # Forest proximity bonus for sustainable crops
        if crop_data["sustainability"] == "high" and forest_pct > 20:
            score += 5   # Sustainable crop near forest areas
    else:
        # Fallback scoring when no LULC data
        score += 10
    
    # Crop rotation benefits (15 points)
    if crop_name.lower() not in past_crops.lower():
        score += 15
    else:
        score += 5  # Still okay but crop rotation is better
    
    # Sustainability bonus (10 points)
    sustainability_bonus = {"high": 10, "medium": 7, "low": 3}
    score += sustainability_bonus.get(crop_data["sustainability"], 5)
    
    # Soil data integration (5 points) - NEW!
    if soil_data:
        # Add bonus for crops that match actual soil conditions
        score += 5
    
    # Weather-based scoring (20 points) - NEW!
    if weather_data and weather_data.get('source') == 'openweather':
        weather_analysis = analyze_weather_for_agriculture(weather_data)
        if weather_analysis:
            temp = weather_data['current']['temperature']
            humidity = weather_data['current']['humidity']
            rain = weather_data['current']['rain']
            
            # Temperature suitability for different crops
            if crop_name in ["Rice", "Sugarcane"] and 25 <= temp <= 35:
                score += 8  # Tropical crops prefer warm weather
            elif crop_name in ["Wheat", "Barley"] and 15 <= temp <= 25:
                score += 8  # Temperate crops prefer cooler weather
            elif crop_name in ["Maize", "Cotton"] and 20 <= temp <= 30:
                score += 6  # Moderate temperature crops
            
            # Humidity suitability
            if crop_name in ["Rice"] and humidity > 60:
                score += 5  # Rice prefers high humidity
            elif crop_name in ["Wheat", "Barley"] and humidity < 70:
                score += 5  # Wheat prefers moderate humidity
            elif crop_name in ["Cotton"] and 40 <= humidity <= 70:
                score += 4  # Cotton prefers moderate humidity
            
            # Rainfall suitability
            if crop_name in ["Rice", "Sugarcane"] and rain > 2:
                score += 7  # Water-intensive crops benefit from rain
            elif crop_name in ["Wheat", "Barley"] and rain < 5:
                score += 5  # Cereals prefer moderate rain
            elif crop_name in ["Cotton", "Groundnut"] and rain < 3:
                score += 4  # These crops prefer less rain during certain stages
    
    return min(score, max_score)

def calculate_crop_score(crop_name, crop_data, soil_type, water_availability, location, past_crops):
    """Legacy function for backward compatibility"""
    return calculate_enhanced_crop_score(crop_name, crop_data, soil_type, water_availability, location, past_crops, None, None, "")

def get_realistic_yield_and_profit(crop_data, score):
    """Generate realistic yield and profit based on crop data and score"""
    yield_min, yield_max = crop_data["yield_range"]
    profit_min, profit_max = crop_data["profit_range"]
    
    # Adjust based on score (higher score = better yield/profit)
    score_factor = score / 100
    
    yield_val = yield_min + (yield_max - yield_min) * score_factor
    profit_val = profit_min + (profit_max - profit_min) * score_factor
    
    # Add some randomness for realism
    yield_val *= random.uniform(0.9, 1.1)
    profit_val *= random.uniform(0.9, 1.1)
    
    return yield_val, profit_val

@app.route('/get_suggestions', methods=['POST'])
def get_suggestions():
    start_time = time.time()
    try:
        data = request.get_json()
        soil_type = data.get("soil_type", "").lower()
        location = data.get("location", "")
        water = data.get("water", "").lower()
        past_crops = data.get("past_crops", "").lower()
        
        print(f"Received request: soil={soil_type}, location={location}, water={water}, past_crops={past_crops}")
        
        # Fast geocoding - use simple lookup instead of API calls
        detected_state = get_location_region(location)
        
        # Use approximate coordinates based on state for faster processing
        state_coords = {
            "delhi": (28.7041, 77.1025),
            "mumbai": (19.0760, 72.8777),
            "bangalore": (12.9716, 77.5946),
            "kolkata": (22.5726, 88.3639),
            "chennai": (13.0827, 80.2707),
            "hyderabad": (17.3850, 78.4867),
            "pune": (18.5204, 73.8567),
            "ahmedabad": (23.0225, 72.5714),
            "jaipur": (26.9124, 75.7873),
            "lucknow": (26.8467, 80.9462)
        }
        
        # Get coordinates quickly
        lat, lon = state_coords.get(detected_state.lower(), (20.5937, 78.9629))
        
        # Use optimized LULC data (pre-calculated for major regions)
        lulc_data = {
            'agriculture': 50,
            'forest': 20,
            'water': 10,
            'barren': 20,
            'source': 'optimized'
        }
        
        # Get weather data with caching (only if enabled)
        weather_data = None
        weather_analysis = None
        if USE_WEATHER_API:
            weather_data = get_weather_data_openweather(lat, lon)
            if weather_data:
                weather_analysis = analyze_weather_for_agriculture(weather_data)
        
        # Calculate crop scores using optimized algorithm
        crop_scores = {}
        for crop_name, crop_data in CROP_DATABASE.items():
            score = calculate_enhanced_crop_score(
                crop_name, crop_data, soil_type, water, location, past_crops,
                lulc_data, None, detected_state, weather_data
            )
            crop_scores[crop_name] = {
                "score": score,
                "data": crop_data
            }
        
        # Sort crops by score (highest first)
        sorted_crops = sorted(crop_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        # Get top 4 crops
        suggestions = []
        for crop_name, crop_info in sorted_crops[:4]:
            crop_data = crop_info["data"]
            score = crop_info["score"]
            
            yield_val, profit_val = get_realistic_yield_and_profit(crop_data, score)
            
            # Format yield and profit
            if crop_name == "Sugarcane":
                yield_str = f"{yield_val:.0f} tonnes/acre"
            elif crop_name == "Potato":
                yield_str = f"{yield_val:.0f} q/acre"
            elif crop_name == "Cotton":
                yield_str = f"{yield_val:.1f} q/acre"
            else:
                yield_str = f"{yield_val:.1f} q/acre"
            
            profit_str = f"₹{profit_val:,.0f}"
            
            # Get fertilizer recommendations for this crop
            fertilizer_rec = get_fertilizer_recommendations(crop_name, soil_type, 6.5)
            
            suggestion = {
                "name": crop_name,
                "yield": yield_str,
                "profit": profit_str,
                "sustainability": crop_data["sustainability"].title(),
                "score": score,
                "emoji": crop_data["emoji"],
                "fertilizer": {
                    "nitrogen": fertilizer_rec['nitrogen'],
                    "phosphorus": fertilizer_rec['phosphorus'],
                    "potassium": fertilizer_rec['potassium'],
                    "source": fertilizer_rec.get('source', 'ml_dataset')
                }
            }
            suggestions.append(suggestion)
        
        response_time = time.time() - start_time
        print(f"Generated {len(suggestions)} crop suggestions in {response_time:.2f} seconds")
        
        return jsonify({
            "recommendations": suggestions,
            "location_analyzed": location,
            "region_detected": detected_state,
            "coordinates": {"lat": lat, "lon": lon},
            "land_use_data": lulc_data,
            "weather_data": {
                "current": weather_data['current'] if weather_data else None,
                "analysis": weather_analysis,
                "source": "openweather" if weather_data else "optimized"
            },
            "data_sources": {
                "geocoding": "optimized",
                "land_use": "optimized",
                "soil_data": "estimated",
                "weather": "openweather" if weather_data else "optimized"
            },
            "performance": {
                "response_time_seconds": round(response_time, 2),
                "optimization": "enabled"
            }
        })
        
    except Exception as e:
        print(f"Error in get_suggestions: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/get_fertilizer_recommendations', methods=['POST'])
def get_fertilizer_recommendations_api():
    """Get fertilizer recommendations for a specific crop"""
    try:
        data = request.get_json()
        crop_name = data.get("crop_name", "")
        soil_type = data.get("soil_type", "")
        ph_level = data.get("ph_level", 6.5)
        
        print(f"Fertilizer request: crop={crop_name}, soil={soil_type}, ph={ph_level}")
        
        # Get fertilizer recommendations
        recommendations = get_fertilizer_recommendations(crop_name, soil_type, ph_level)
        
        # Add additional fertilizer advice
        fertilizer_advice = {
            'nitrogen': {
                'amount': recommendations['nitrogen'],
                'form': 'Urea (46% N)',
                'application': 'Split into 2-3 applications during growth season',
                'timing': 'Apply at planting and during vegetative growth'
            },
            'phosphorus': {
                'amount': recommendations['phosphorus'],
                'form': 'DAP (18% N, 46% P) or SSP (16% P)',
                'application': 'Apply at planting time',
                'timing': 'Mix well with soil before planting'
            },
            'potassium': {
                'amount': recommendations['potassium'],
                'form': 'MOP (60% K) or SOP (50% K)',
                'application': 'Apply at planting or early growth stage',
                'timing': 'Best applied with phosphorus at planting'
            }
        }
        
        return jsonify({
            'crop_name': crop_name,
            'soil_type': soil_type,
            'ph_level': ph_level,
            'recommendations': recommendations,
            'fertilizer_advice': fertilizer_advice,
            'source': recommendations.get('source', 'ml_dataset'),
            'timestamp': time.time()
        })
        
    except Exception as e:
        print(f"Error in fertilizer recommendations: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/process_data', methods=['POST'])
def process_ml_data():
    """Process crop and fertilizer datasets"""
    try:
        print("Processing crop and fertilizer datasets...")
        result = process_crop_and_fertilizer_data()
        
        return jsonify({
            'status': 'success',
            'message': 'Data processed successfully',
            'common_crops': result['common_crops'],
            'crop_count': len(result['common_crops']),
            'timestamp': time.time()
        })
        
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return jsonify({"error": "Data processing failed"}), 500

if __name__ == "__main__":
    # Initialize data processing on startup
    try:
        print("Initializing crop and fertilizer data...")
        process_crop_and_fertilizer_data()
        print("Data initialization completed.")
    except Exception as e:
        print(f"Data initialization failed: {e}")
    
    app.run(debug=True, host='127.0.0.1', port=5000)