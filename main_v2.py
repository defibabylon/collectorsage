import os
import json
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS
from utils.image_processing import process_comic_image
from utils.report_generation import generate_qualitative_report
from utils.ebay import fetch_ebay_data, calculate_sales_trend
from utils.database import fetch_database_info
from utils.currency_conversion import convert_currency
from config import UPLOAD_FOLDER
import anthropic
import redis
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s [%(levelname)s] %(message)s', 
                    handlers=[logging.FileHandler("app.log"), 
                              logging.StreamHandler()])

load_dotenv()  # This loads the variables from .env into the environment

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

try:
    # Ensure the environment variable name is correct and print it to verify
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    logging.debug(f"API Key: {anthropic_api_key}")
    if not anthropic_api_key:
        raise ValueError("API Key is not set.")

    # Initialize the Anthropic client with the API key
    client = anthropic.Client(api_key=anthropic_api_key)

    google_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if google_credentials and os.path.exists(google_credentials):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_credentials
    else:
        # For cloud deployment, we'll use JSON content from environment variable
        google_creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if google_creds_json:
            # Create a temporary credentials file
            import tempfile
            import json
            
            temp_creds = tempfile.NamedTemporaryFile(delete=False)
            with open(temp_creds.name, 'w') as f:
                f.write(google_creds_json)
            
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_creds.name

    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    cache = redis.from_url(redis_url)

    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:8000/callback')

except Exception as e:
    logging.exception("Failed during startup or dependency injection")

@app.get("/")
def root():
    return "Hello, World!"

@app.get("/test")
def test_endpoint():
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

    try:
        result, search_query = process_comic_image(image_path)

        if result:
            title = result['title']
            issue_number = result['issue_number']
            year = result['year']

            logging.debug(f"Comic details - Title: {title}, Issue Number: {issue_number}, Year: {year}")

            # Fetch database prices and metadata in a single query
            database_prices, metadata = fetch_database_info(title, issue_number)
            logging.debug(f"Database Prices: {database_prices}")

            if database_prices:
                database_avg_price = sum(database_prices) / len(database_prices)
            else:
                database_avg_price = 0.0

            logging.debug(f"Database Average Price: £{database_avg_price:.2f}")

            # Fetch eBay data
            ebay_data = fetch_ebay_data(search_query)
            if not ebay_data or 'itemSummaries' not in ebay_data:
                return jsonify({'error': 'No eBay data found or missing itemSummaries'}), 404

            items = ebay_data.get('itemSummaries', [])
            items = sorted(items, key=lambda x: float(x['price']['value']), reverse=True)

            prices = [convert_currency(float(item.get('price', {}).get('value', 0)), item.get('price', {}).get('currency', 'USD')) for item in items if item.get('price', {}).get('value')]

            if not prices:
                return jsonify({'error': 'No valid prices found'}), 404

            avg_price = sum(prices) / len(prices)
            logging.debug(f"Average eBay Price: £{avg_price:.2f}")

            sold_dates = [datetime.strptime(item['itemEndDate'], '%Y-%m-%dT%H:%M:%S.%fZ') for item in items if 'itemEndDate' in item]
            sales_trend = calculate_sales_trend(sold_dates)


            qualitative_report = generate_qualitative_report(
                title, 
                issue_number, 
                year, 
                avg_price, 
                database_avg_price, 
                ebay_data, 
                client, 
                sales_trend,
                metadata
            )

            comic_details = {
                'title': title,
                'issueNumber': issue_number,
                'year': year
            }
            return jsonify({'comicDetails': comic_details, 'report': qualitative_report})
        else:
            return jsonify({'error': 'Failed to process image'}), 500

    except FileNotFoundError:
        return jsonify({'error': 'Image file not found'}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.exception("Error processing image")
        return jsonify({'error': 'An unexpected error occurred'}), 500
    
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
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logging.exception("Error starting Flask app")
