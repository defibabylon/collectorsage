import os
import time
import requests
import json
import redis
import re
import google.generativeai as genai
from PIL import Image
import anthropic
from tqdm import tqdm
from dotenv import load_dotenv
from flask import Flask, request, jsonify, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s [%(levelname)s] %(message)s', 
                    handlers=[logging.FileHandler("app.log"), 
                              logging.StreamHandler()])

load_dotenv()  # This loads the variables from .env into the environment

try:
    # Ensure the environment variable name is correct and print it to verify
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    logging.debug(f"API Key: {anthropic_api_key}")
    if not anthropic_api_key:
        raise ValueError("API Key is not set.")

    # Initialize the Anthropic client with the API key
    client = anthropic.Client(api_key=anthropic_api_key)

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/mnt/d/projects/2024/q3/collectorsage/collectorsage.json'

    cache = redis.Redis(host='localhost', port=6379, db=0)

    CLIENT_ID = 'TashomaV-Collecto-PRD-0ac16becc-806a9ce2'
    CLIENT_SECRET = 'PRD-ac16becceb3c-f305-48bd-be2a-a943'
    REDIRECT_URI = 'http://localhost:8000/callback'

    app = Flask(__name__)
    CORS(app)
    UPLOAD_FOLDER = '/mnt/d/projects/2024/q3/collectorsage/uploads'
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
except Exception as e:
    logging.exception("Failed during startup or dependency injection")

# Load the JSON databases
db_path = r"D:\projects\2024\Q3\collectorsage\databases"
with open(os.path.join(db_path, "30thcenturycomics-1.json"), 'r', encoding='utf-8') as f:
    db_30thcenturycomics = json.load(f)

with open(os.path.join(db_path, "SilverAcre-1.json"), 'r', encoding='utf-8') as f:
    db_silveracre = json.load(f)

# Get eBay OAuth token
def get_ebay_oauth_token():
    logging.info("Fetching eBay OAuth token...")
    try:
        token_url = 'https://api.ebay.com/identity/v1/oauth2/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'client_credentials',
            'redirect_uri': REDIRECT_URI,
            'scope': 'https://api.ebay.com/oauth/api_scope'
        }
        response = requests.post(token_url, headers=headers, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
        response.raise_for_status()
        token = response.json().get('access_token')
        cache.set('EBAY_OAUTH_TOKEN', token, ex=3600)
        return token
    except Exception as e:
        logging.exception("Failed to fetch eBay OAuth token")
        return None

# Recognize comic issue using Gemini
def recognize_comic_issue_with_gemini(image_path):
    logging.info("Recognizing comic issue using Gemini...")
    try:
        img = Image.open(image_path)
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content(img)
        recognized_text = response.text
        logging.debug(f"Recognized text: {recognized_text}")
        return recognized_text
    except Exception as e:
        logging.exception("Error recognizing comic issue")
        return None

# Extract relevant text using another instance of Gemini
def extract_relevant_text_with_gemini(description):
    logging.info("Extracting relevant text using Gemini...")
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        Extract the title, issue number, and year from the following comic book description:

        "{description}"
        
        Respond in the format: Title: [title], Issue Number: [issue number], Year: [year]
        """
        response = model.generate_content(prompt)
        extracted_text = response.text
        logging.debug(f"Extracted text: {extracted_text}")
        return extracted_text
    except Exception as e:
        logging.exception("Error extracting relevant text")
        return None

# Fetch data from eBay
def fetch_ebay_data(query):
    logging.info(f"Fetching eBay data for query: {query}")
    try:
        token = cache.get('EBAY_OAUTH_TOKEN')
        if not token:
            token = get_ebay_oauth_token()
        if not token:
            return {}

        response = requests.get(
            'https://api.ebay.com/buy/browse/v1/item_summary/search',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            params={
                'q': query,
                'category_ids': '158671',
                'filter': 'price:[10..],priceCurrency:GBP',
                'item_location_country': 'GB',
                'item_condition': '3000',
                'buying_options': 'FIXED_PRICE',
                'sold_items_only': 'true'
            }
        )
        response.raise_for_status()
        data = response.json()
        cache.set(query, json.dumps(data), ex=3600)
        return data
    except Exception as e:
        logging.exception(f"Error fetching eBay data for query: {query}")
        return {}

# Convert currency to GBP
def convert_currency(amount, from_currency, to_currency='GBP'):
    logging.info(f"Converting currency from {from_currency} to {to_currency}...")
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        response.raise_for_status()
        rates = response.json().get('rates', {})
        if from_currency == 'USD':
            return amount / rates['GBP']
        elif from_currency == 'CAD':
            return amount / rates['GBP'] * 1.71
        return amount
    except Exception as e:
        logging.exception(f"Error converting currency from {from_currency} to {to_currency}")
        return amount

def fetch_database_prices(title, issue_number):
    logging.info(f"Fetching database prices for {title} #{issue_number}...")
    try:
        # Query 30th Century Comics database
        prices_30thcentury = [comic['price'] for comic in db_30thcenturycomics if comic['title'].lower() == title.lower() and comic['issue_number'] == issue_number]

        # Query Silver Acre database
        prices_silveracre = [comic['price'] for comic in db_silveracre if comic['title'].lower() == title.lower() and comic['issue_number'] == issue_number]

        return prices_30thcentury + prices_silveracre
    except Exception as e:
        logging.exception("Error fetching database prices")
        return []

# Generate a qualitative report
def generate_qualitative_report(title, issue_number, year, avg_price, database_avg_price, ebay_data):
    logging.info("Generating qualitative report...")
    try:
        description = f"Title: {title}\nIssue Number: {issue_number}\nYear: {year}\nAverage Price: £{avg_price:.2f}\nDatabase Average Price: £{database_avg_price:.2f}\n"
        
        items = ebay_data.get('itemSummaries', [])
        detailed_items = []

        for item in items:
            title = item.get('title', 'Unknown title')
            price = item.get('price', {}).get('value', 'Unknown price')
            currency = item.get('price', {}).get('currency', 'Unknown currency')
            condition = item.get('condition', 'Unknown condition')
            grade = item.get('conditionId', 'Unknown grade')

            price_gbp = convert_currency(float(price), currency) if currency != 'GBP' else float(price)

            detailed_items.append({
                'title': title,
                'price_gbp': price_gbp,
                'condition': condition,
                'grade': grade
            })

        for item in detailed_items:
            description += f"\nItem: {item['title']}\nPrice (GBP): £{item['price_gbp']:.2f}\nCondition: {item['condition']}\nGrade: {item['grade']}\n"

        prompt = f"""
        \n\nHuman: You are an expert comic book dealer. Take the following price information from eBay and weigh it against the price for the same comic book found in the SilverAcre and 30th Century Comics knowledgebase and write a concise short price report on the comic book based on the template below:

        [Comic book name and volume]
        Impact: [1-5 stars]
        Rarity: [1-5 stars]
        Value: [1-5 stars]
        Story: [1-5 stars]
        Artwork: [1-5 stars]
        Price estimate graded: £X.XX
        Price estimate non-graded: £X.XX

        [short expert justification]

        Here is the comic book data:
        {description}
        \n\nAssistant:
        """

        response = client.completions.create(
            model="claude-v1",
            max_tokens_to_sample=300,
            temperature=0.7,
            prompt=prompt
        )

        # Access the correct attribute of the response object
        qualitative_report = response.completion

        # Convert prices in the report to GBP
        qualitative_report = re.sub(r'\$(\d[\d,.]*)', lambda x: f"£{convert_currency(float(x.group(1).replace(',', '')), 'USD'):.2f}", qualitative_report)
        
        return qualitative_report
    except Exception as e:
        logging.exception("Error generating qualitative report")
        return ""

# Process comic image
def process_comic_image(image_path, max_retries=3, retry_delay=5):
    logging.info("Processing comic image...")
    retry_count = 0
    while retry_count < max_retries:
        try:
            comic_issue_description = recognize_comic_issue_with_gemini(image_path)
            if not comic_issue_description:
                logging.warning("No comic issue recognized.")
                retry_count += 1
                logging.info(f"Retrying in {retry_delay} seconds... (Attempt {retry_count}/{max_retries})")
                time.sleep(retry_delay)
                continue

            relevant_text = extract_relevant_text_with_gemini(comic_issue_description)
            match = re.search(r'Title: (.*?), Issue Number: (.*?), Year: (.*?)$', relevant_text)
            if not match:
                logging.warning(f"Error: Could not extract relevant text from '{relevant_text}'")
                retry_count += 1
                logging.info(f"Retrying in {retry_delay} seconds... (Attempt {retry_count}/{max_retries})")
                time.sleep(retry_delay)
                continue

            title, issue_number, year = match.groups()
            ebay_data = fetch_ebay_data(f"{title} {issue_number} {year}")
            if not ebay_data or 'itemSummaries' not in ebay_data:
                logging.warning("No eBay data found or 'itemSummaries' key is missing.")
                retry_count += 1
                logging.info(f"Retrying in {retry_delay} seconds... (Attempt {retry_count}/{max_retries})")
                time.sleep(retry_delay)
                continue

            items = ebay_data.get('itemSummaries', [])
            items = sorted(items, key=lambda x: float(x['price']['value']), reverse=True)

            prices = []
            for item in tqdm(items, desc="Processing eBay items"):
                price_info = item.get('price', {})
                amount = price_info.get('value')
                currency = price_info.get('currency')
                if amount and currency:
                    converted_price = convert_currency(float(amount), currency)
                    prices.append(converted_price)

            if not prices:
                logging.warning("No valid prices found.")
                retry_count += 1
                logging.info(f"Retrying in {retry_delay} seconds... (Attempt {retry_count}/{max_retries})")
                time.sleep(retry_delay)
                continue

            avg_price = sum(prices) / len(prices)
            database_prices = fetch_database_prices(title, issue_number)

            if database_prices:
                database_avg_price = sum(database_prices) / len(database_prices)
            else:
                database_avg_price = 0.0

            qualitative_report = generate_qualitative_report(title, issue_number, year, avg_price, database_avg_price, ebay_data)
            logging.info(f"Qualitative Report: {qualitative_report}")
            return {"title": title, "issue_number": issue_number, "year": year, "qualitative_report": qualitative_report}
        except Exception as e:
            logging.exception("Error processing comic image")
            retry_count += 1
            logging.info(f"Retrying in {retry_delay} seconds... (Attempt {retry_count}/{max_retries})")
            time.sleep(retry_delay)

    logging.error("Max retries reached. Unable to process the comic image.")
    return None

@app.get("/")
def root():
    return "Hello, World!"

@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint is working"}

@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)

    # Call the existing process_comic_image function
    result = process_comic_image(image_path)

    if result:
        comic_details = {
            'title': result['title'],
            'issueNumber': result['issue_number'],
            'year': result['year']
        }
        report = result['qualitative_report']
        return jsonify({'comicDetails': comic_details, 'report': report})
    else:
        return jsonify({'error': 'Failed to process image'}), 500

# Route to list all routes
@app.get("/routes")
def list_routes():
    import urllib
    routes = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = f"<{arg}>"
        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.parse.unquote(f"{rule.endpoint:50s} {methods:20s} {url}")
        routes.append(line)
    return jsonify(routes)

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        logging.exception("Error starting Flask app")
