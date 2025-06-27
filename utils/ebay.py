import os
import json
import requests
import logging
from dotenv import load_dotenv
import redis
from datetime import datetime, timedelta

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:8000/callback')

redis_url = os.getenv('REDIS_URL')
if redis_url and redis_url.strip():
    try:
        cache = redis.from_url(redis_url)
    except Exception as e:
        logging.warning(f"Failed to connect to Redis in eBay module: {e}")
        cache = None
else:
    cache = None

def get_ebay_oauth_token():
    logging.info("Fetching eBay OAuth token...")
    try:
        token_url = 'https://api.ebay.com/identity/v1/oauth2/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'client_credentials',
            'scope': 'https://api.ebay.com/oauth/api_scope'
        }
        response = requests.post(token_url, headers=headers, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
        response.raise_for_status()
        token = response.json().get('access_token')
        if cache:
            cache.set('EBAY_OAUTH_TOKEN', token, ex=3600)
        return token
    except requests.exceptions.RequestException as e:
        logging.exception(f"Error fetching eBay OAuth token: {e}")
        return None

def fetch_ebay_data(query):
    logging.info(f"Fetching eBay data for query: {query}")
    try:
        token = None
        if cache:
            token = cache.get('EBAY_OAUTH_TOKEN')
        if not token:
            token = get_ebay_oauth_token()
        if not token:
            return {}

        url = 'https://api.ebay.com/buy/browse/v1/item_summary/search'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        params = {
            'q': query,
            'category_ids': '158671',
            'filter': 'price:[10..],priceCurrency:GBP',
            'item_location_country': 'GB',
            'item_condition': '3000',
            'buying_options': 'FIXED_PRICE',
            'sold_items_only': 'true'
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if cache:
            cache.set(query, json.dumps(data), ex=3600)
        return data
    except requests.exceptions.RequestException as e:
        logging.exception(f"Error fetching eBay data for query: {query} - {e}")
        return {}

def calculate_sales_trend(items):
    """Calculate sales trend from eBay items"""
    if not items:
        return "Stable"

    # For now, return a simple trend based on number of items
    # In a real implementation, we would extract actual sale dates
    # from the eBay API response if available

    num_items = len(items)
    if num_items > 20:
        return "High Activity"
    elif num_items > 10:
        return "Moderate Activity"
    elif num_items > 5:
        return "Low Activity"
    else:
        return "Limited Activity"
