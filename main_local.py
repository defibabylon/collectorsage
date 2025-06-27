#!/usr/bin/env python3
"""
Local development version of CollectorSage backend
Optimized for testing speed improvements locally
"""

import os
import json
import logging
import time
import concurrent.futures
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
from utils.image_processing import process_comic_image, process_comic_image_fast
from utils.report_generation import generate_qualitative_report
from utils.ebay import fetch_ebay_data, calculate_sales_trend
from utils.database import fetch_database_info
from utils.currency_conversion import convert_currency

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s [%(levelname)s] %(message)s')

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Local upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Verify API keys
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
if not anthropic_api_key:
    logging.error("ANTHROPIC_API_KEY not found in environment variables")
else:
    logging.info("Anthropic API key loaded successfully")

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'CollectorSage Local Backend is running',
        'version': 'local-dev',
        'endpoints': [
            '/process_image',
            '/process_image_fast',
            '/test'
        ]
    })

@app.route('/test')
def test():
    """Simple test endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Test endpoint working',
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'anthropic_key_set': bool(anthropic_api_key)
    })

@app.route('/process_image', methods=['POST'])
def process_image():
    """Original image processing endpoint (slower)"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)

    try:
        start_time = time.time()
        logging.info(f"Processing image (regular): {image_path}")

        # Use legacy processing (Google Vision + Claude)
        from utils.image_processing import process_comic_image_legacy
        result, search_query = process_comic_image_legacy(image_path)
        image_processing_time = time.time() - start_time
        
        if result:
            title = result['title']
            issue_number = result['issue_number']
            year = result['year']

            # Sequential data fetching (slower)
            database_start = time.time()
            database_prices, metadata = fetch_database_info(title, issue_number)
            database_time = time.time() - database_start

            ebay_start = time.time()
            ebay_data = fetch_ebay_data(search_query)
            ebay_time = time.time() - ebay_start

            if not ebay_data or 'itemSummaries' not in ebay_data:
                return jsonify({'error': 'No eBay data found'}), 404

            # Process results
            items = ebay_data.get('itemSummaries', [])
            items = sorted(items, key=lambda x: float(x['price']['value']), reverse=True)

            prices = [convert_currency(float(item.get('price', {}).get('value', 0)),
                     item.get('price', {}).get('currency', 'USD')) for item in items
                     if item.get('price', {}).get('value')]

            if prices:
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)
                sales_trend = calculate_sales_trend(items)

                # Try to get year from metadata if not found in image
                display_year = year
                if (not year or year == 'N/A') and metadata and isinstance(metadata, list) and metadata:
                    meta_year = metadata[0].get('year')
                    if meta_year:
                        display_year = str(meta_year)
                        logging.info(f"Using year from metadata: {display_year}")

                comic_details = {
                    'title': title,
                    'issueNumber': issue_number,  # Fixed: camelCase for frontend
                    'year': display_year,
                    'min_price': f"{min_price:.2f}",
                    'max_price': f"{max_price:.2f}",
                    'avg_price': f"{avg_price:.2f}",
                    'sales_trend': sales_trend,
                    'database_avg_price': f"{sum(database_prices) / len(database_prices):.2f}" if database_prices else "0.00",
                    'total_listings': len(items)
                }

                # Import anthropic client
                import anthropic
                client = anthropic.Client(api_key=anthropic_api_key)

                database_avg_price = sum(database_prices) / len(database_prices) if database_prices else 0.0

                qualitative_report = generate_qualitative_report(
                    title, issue_number, display_year, avg_price, database_avg_price,
                    ebay_data, client, sales_trend, metadata
                )

                total_time = time.time() - start_time
                logging.info(f"Regular processing completed in {total_time:.2f}s")

                return jsonify({
                    'comicDetails': comic_details,
                    'report': qualitative_report,
                    'processingTime': f"{total_time:.2f}s",
                    'breakdown': {
                        'image_processing': f"{image_processing_time:.2f}s",
                        'database_fetch': f"{database_time:.2f}s",
                        'ebay_fetch': f"{ebay_time:.2f}s"
                    }
                })
            else:
                return jsonify({'error': 'No valid price data found'}), 404
        else:
            return jsonify({'error': 'Failed to process image'}), 500

    except Exception as e:
        logging.exception("Error in regular image processing")
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

@app.route('/process_image_fast', methods=['POST'])
def process_image_fast():
    """Optimized image processing endpoint (faster)"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)

    try:
        start_time = time.time()
        logging.info(f"Processing image (fast): {image_path}")

        # Fast image processing (Claude only, optimized)
        result, search_query = process_comic_image_fast(image_path)
        image_processing_time = time.time() - start_time
        
        if result:
            title = result['title']
            issue_number = result['issue_number']
            year = result['year']

            # Parallel data fetching (faster)
            parallel_start = time.time()

            def fetch_database_data():
                return fetch_database_info(title, issue_number)

            def fetch_ebay_data_wrapper():
                return fetch_ebay_data(search_query)

            # Execute database and eBay fetching in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                database_future = executor.submit(fetch_database_data)
                ebay_future = executor.submit(fetch_ebay_data_wrapper)

                # Get results
                database_prices, metadata = database_future.result()
                ebay_data = ebay_future.result()

            parallel_time = time.time() - parallel_start

            if not ebay_data or 'itemSummaries' not in ebay_data:
                return jsonify({'error': 'No eBay data found'}), 404

            # Process results (same as regular)
            items = ebay_data.get('itemSummaries', [])
            items = sorted(items, key=lambda x: float(x['price']['value']), reverse=True)

            prices = [convert_currency(float(item.get('price', {}).get('value', 0)),
                     item.get('price', {}).get('currency', 'USD')) for item in items
                     if item.get('price', {}).get('value')]

            if prices:
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)
                sales_trend = calculate_sales_trend(items)

                # Try to get year from metadata if not found in image
                display_year = year
                if (not year or year == 'N/A') and metadata and isinstance(metadata, list) and metadata:
                    meta_year = metadata[0].get('year')
                    if meta_year:
                        display_year = str(meta_year)
                        logging.info(f"Using year from metadata: {display_year}")

                comic_details = {
                    'title': title,
                    'issueNumber': issue_number,  # Fixed: camelCase for frontend
                    'year': display_year,
                    'min_price': f"{min_price:.2f}",
                    'max_price': f"{max_price:.2f}",
                    'avg_price': f"{avg_price:.2f}",
                    'sales_trend': sales_trend,
                    'database_avg_price': f"{sum(database_prices) / len(database_prices):.2f}" if database_prices else "0.00",
                    'total_listings': len(items)
                }

                # Import anthropic client
                import anthropic
                client = anthropic.Client(api_key=anthropic_api_key)

                database_avg_price = sum(database_prices) / len(database_prices) if database_prices else 0.0

                qualitative_report = generate_qualitative_report(
                    title, issue_number, display_year, avg_price, database_avg_price,
                    ebay_data, client, sales_trend, metadata
                )

                total_time = time.time() - start_time
                logging.info(f"Fast processing completed in {total_time:.2f}s")

                return jsonify({
                    'comicDetails': comic_details,
                    'report': qualitative_report,
                    'processingTime': f"{total_time:.2f}s",
                    'breakdown': {
                        'image_processing': f"{image_processing_time:.2f}s",
                        'parallel_fetch': f"{parallel_time:.2f}s"
                    }
                })
            else:
                return jsonify({'error': 'No valid price data found'}), 404
        else:
            return jsonify({'error': 'Failed to process image'}), 500

    except Exception as e:
        logging.exception("Error in fast image processing")
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting CollectorSage Local Backend...")
    print("📁 Upload folder:", UPLOAD_FOLDER)
    print("🔑 Anthropic API key:", "✅ Set" if anthropic_api_key else "❌ Missing")
    print("🌐 Server will be available at: http://127.0.0.1:8000")
    print("📋 Available endpoints:")
    print("   GET  /           - Health check")
    print("   GET  /test       - Simple test")
    print("   POST /process_image      - Regular processing")
    print("   POST /process_image_fast - Fast processing")
    
    app.run(host='127.0.0.1', port=8000, debug=True)
