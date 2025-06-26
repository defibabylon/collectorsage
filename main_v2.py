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

    redis_url = os.getenv('REDIS_URL')
    if redis_url and redis_url.strip():
        try:
            cache = redis.from_url(redis_url)
            logging.info("Redis cache connected successfully")
        except Exception as e:
            logging.warning(f"Failed to connect to Redis: {e}. Continuing without cache.")
            cache = None
    else:
        logging.info("No Redis URL provided. Running without cache.")
        cache = None

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

@app.get("/debug")
def debug_endpoint():
    """Debug endpoint to check environment variables and credentials"""
    debug_info = {
        "anthropic_key_set": bool(os.getenv('ANTHROPIC_API_KEY')),
        "google_creds_json_set": bool(os.getenv('GOOGLE_CREDENTIALS_JSON')),
        "google_app_creds_set": bool(os.getenv('GOOGLE_APPLICATION_CREDENTIALS')),
        "upload_folder": app.config.get('UPLOAD_FOLDER'),
        "upload_folder_exists": os.path.exists(app.config.get('UPLOAD_FOLDER', '')),
        "ebay_client_id_set": bool(os.getenv('CLIENT_ID')),
        "ebay_client_secret_set": bool(os.getenv('CLIENT_SECRET')),
        "pinecone_api_key_set": bool(os.getenv('PINECONE_API_KEY')),
        "redis_url": os.getenv('REDIS_URL', 'Not set')
    }
    return jsonify(debug_info)

@app.get("/test-vision")
def test_vision_endpoint():
    """Test endpoint to check if Google Vision client can be initialized"""
    try:
        from utils.image_processing import vision_client
        if vision_client:
            return jsonify({'status': 'success', 'message': 'Google Vision client initialized successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Google Vision client not available'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error initializing Google Vision client: {str(e)}'})

@app.get("/test-anthropic")
def test_anthropic_endpoint():
    """Test endpoint to check if Anthropic client can be initialized"""
    try:
        import anthropic
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_api_key:
            client = anthropic.Client(api_key=anthropic_api_key)
            return jsonify({'status': 'success', 'message': 'Anthropic client initialized successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'ANTHROPIC_API_KEY not set'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error initializing Anthropic client: {str(e)}'})

@app.route('/test-process', methods=['POST'])
def test_process_image():
    """Test endpoint to simulate image processing without actual image"""
    try:
        # Test the image processing pipeline with mock data
        logging.info("Testing image processing pipeline...")

        # Mock comic details
        mock_result = {
            'title': 'Test Comic',
            'issue_number': '1',
            'year': '2023'
        }
        mock_search_query = 'Test Comic 1 2023'

        logging.info(f"Mock processing result: {mock_result}, search_query: {mock_search_query}")

        title = mock_result['title']
        issue_number = mock_result['issue_number']
        year = mock_result['year']

        # Test database fetch
        from utils.database import fetch_database_info
        database_prices, metadata = fetch_database_info(title, issue_number)
        logging.info(f"Database fetch successful: {len(database_prices)} prices, {len(metadata) if metadata else 0} metadata")

        # Test eBay fetch
        from utils.ebay import fetch_ebay_data
        ebay_data = fetch_ebay_data(mock_search_query)
        logging.info(f"eBay fetch successful: {len(ebay_data.get('itemSummaries', []))} items")

        return jsonify({
            'status': 'success',
            'message': 'Image processing pipeline test completed successfully',
            'mock_data': {
                'comic_details': mock_result,
                'database_prices_count': len(database_prices),
                'metadata_count': len(metadata) if metadata else 0,
                'ebay_items_count': len(ebay_data.get('itemSummaries', []))
            }
        })

    except Exception as e:
        logging.exception("Error in test image processing pipeline")
        return jsonify({
            'status': 'error',
            'message': f'Error in test processing: {str(e)}',
            'error_type': type(e).__name__
        }), 500

@app.route('/test-image-processing', methods=['GET'])
def test_image_processing():
    """Test endpoint to check image processing with a sample image"""
    try:
        # Check if there are any existing images in the uploads folder
        upload_folder = app.config['UPLOAD_FOLDER']
        if os.path.exists(upload_folder):
            image_files = [f for f in os.listdir(upload_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            if image_files:
                # Use the first available image
                test_image_path = os.path.join(upload_folder, image_files[0])
                logging.info(f"Testing image processing with: {test_image_path}")

                result, search_query = process_comic_image(test_image_path)

                return jsonify({
                    'status': 'success',
                    'message': f'Image processing test completed with {image_files[0]}',
                    'result': result,
                    'search_query': search_query
                })
            else:
                return jsonify({
                    'status': 'info',
                    'message': 'No test images available in upload folder'
                })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Upload folder does not exist'
            })

    except Exception as e:
        logging.exception("Error in test image processing")
        return jsonify({
            'status': 'error',
            'message': f'Error in test image processing: {str(e)}',
            'error_type': type(e).__name__
        }), 500

@app.route('/test-simple-processing', methods=['GET'])
def test_simple_processing():
    """Test endpoint to check basic image processing components"""
    try:
        # Test 1: Import check
        logging.info("Testing imports...")
        from utils.image_processing import vision_client, get_google_credentials
        from PIL import Image
        import io
        import base64

        # Test 2: Create a simple test image
        logging.info("Creating test image...")
        test_image = Image.new('RGB', (100, 100), color='white')
        img_buffer = io.BytesIO()
        test_image.save(img_buffer, format='JPEG')
        img_buffer.seek(0)

        # Test 3: Save test image to upload folder
        test_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'test_image.jpg')
        with open(test_image_path, 'wb') as f:
            f.write(img_buffer.getvalue())
        logging.info(f"Test image saved to: {test_image_path}")

        # Test 4: Try to process the test image
        logging.info("Testing image processing...")
        result, search_query = process_comic_image(test_image_path)

        # Clean up
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

        return jsonify({
            'status': 'success',
            'message': 'Simple image processing test completed',
            'result': result,
            'search_query': search_query,
            'vision_client_available': vision_client is not None
        })

    except Exception as e:
        logging.exception("Error in simple image processing test")
        import traceback
        return jsonify({
            'status': 'error',
            'message': f'Error in simple processing test: {str(e)}',
            'error_type': type(e).__name__,
            'traceback': traceback.format_exc()
        }), 500

@app.route('/debug-image-processing', methods=['GET'])
def debug_image_processing():
    """Debug endpoint to test each step of image processing"""
    try:
        # Check if there are any existing images in the uploads folder
        upload_folder = app.config['UPLOAD_FOLDER']
        if os.path.exists(upload_folder):
            image_files = [f for f in os.listdir(upload_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            if image_files:
                # Use the first available image
                test_image_path = os.path.join(upload_folder, image_files[0])
                logging.info(f"Debug testing image processing with: {test_image_path}")

                # Test Google Vision step by step
                from utils.image_processing import recognize_comic_issue_with_google_vision, get_comic_details_with_claude

                # Step 1: Test Google Vision
                recognized_text = recognize_comic_issue_with_google_vision(test_image_path)

                # Step 2: Test Claude if we have text
                comic_details = None
                if recognized_text:
                    comic_details = get_comic_details_with_claude(test_image_path)

                return jsonify({
                    'status': 'success',
                    'test_image': image_files[0],
                    'step1_google_vision': {
                        'text_recognized': bool(recognized_text),
                        'text_length': len(recognized_text) if recognized_text else 0,
                        'text_preview': recognized_text[:200] if recognized_text else None
                    },
                    'step2_claude_api': {
                        'details_extracted': bool(comic_details),
                        'details': comic_details
                    }
                })
            else:
                return jsonify({
                    'status': 'info',
                    'message': 'No test images available in upload folder'
                })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Upload folder does not exist'
            })

    except Exception as e:
        logging.exception("Error in debug image processing")
        return jsonify({
            'status': 'error',
            'message': f'Error in debug image processing: {str(e)}',
            'error_type': type(e).__name__
        }), 500

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
        logging.info(f"Processing image: {image_path}")
        logging.info(f"Image file size: {os.path.getsize(image_path)} bytes")

        # Test if we can read the image file
        try:
            with open(image_path, 'rb') as f:
                content = f.read(100)  # Read first 100 bytes
            logging.info(f"Successfully read image file, first 10 bytes: {content[:10]}")
        except Exception as e:
            logging.error(f"Failed to read image file: {e}")
            return jsonify({'error': f'Failed to read uploaded image: {str(e)}'}), 500

        result, search_query = process_comic_image(image_path)
        logging.info(f"Image processing result: {result}, search_query: {search_query}")

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
            logging.error("Failed to process image - no result returned from process_comic_image")
            return jsonify({'error': 'Failed to process image. This could be due to Google Vision API issues or the image not containing recognizable comic book text.'}), 500

    except FileNotFoundError as e:
        logging.error(f"Image file not found: {e}")
        return jsonify({'error': 'Image file not found'}), 404
    except ValueError as e:
        logging.error(f"ValueError in image processing: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.exception("Error processing image")
        error_message = f"An unexpected error occurred: {str(e)}"
        logging.error(f"Detailed error: {error_message}")

        # Check if it's a Google Vision API error
        if "google" in str(e).lower() or "vision" in str(e).lower():
            error_message = "Google Vision API error. Please check your Google Cloud credentials configuration."
        # Check if it's an Anthropic API error
        elif "anthropic" in str(e).lower() or "claude" in str(e).lower():
            error_message = "Anthropic Claude API error. Please check your API key configuration."

        return jsonify({'error': error_message}), 500
    
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
