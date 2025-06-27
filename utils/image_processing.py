import anthropic
import base64
import os
import re
import json
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image
import io
import asyncio
import concurrent.futures
import time

# Initialize Google Vision client
def get_google_credentials():
    """Get Google Cloud credentials from environment variables or file."""
    # First, try to use GOOGLE_APPLICATION_CREDENTIALS if it's set (for local development)
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS') and os.path.exists(os.getenv('GOOGLE_APPLICATION_CREDENTIALS')):
        return None  # Let the client use default credentials

    # Try to use GOOGLE_CREDENTIALS_JSON environment variable (for deployment)
    google_creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if google_creds_json:
        # Parse the JSON and create credentials from it
        try:
            # Try to handle common formatting issues
            google_creds_json = google_creds_json.strip()

            # If the JSON is wrapped in quotes, remove them
            if google_creds_json.startswith('"') and google_creds_json.endswith('"'):
                google_creds_json = google_creds_json[1:-1]

            # Replace escaped quotes
            google_creds_json = google_creds_json.replace('\\"', '"')

            creds_info = json.loads(google_creds_json)
            credentials = service_account.Credentials.from_service_account_info(creds_info)
            print("Successfully loaded Google Cloud credentials from GOOGLE_CREDENTIALS_JSON environment variable")
            return credentials
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing GOOGLE_CREDENTIALS_JSON: {e}")
            print(f"First 100 characters of credentials: {google_creds_json[:100]}...")
            # Fall through to try individual environment variables

    # Try to construct credentials from individual environment variables
    google_private_key = os.getenv('GOOGLE_PRIVATE_KEY')
    google_client_email = os.getenv('GOOGLE_CLIENT_EMAIL')
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_private_key_id = os.getenv('GOOGLE_PRIVATE_KEY_ID')

    if all([google_private_key, google_client_email, google_client_id, google_private_key_id]):
        try:
            # Construct the credentials JSON from individual environment variables
            creds_info = {
                "type": "service_account",
                "project_id": "resolute-casing-389404",  # Your project ID
                "private_key_id": google_private_key_id,
                "private_key": google_private_key.replace('\\n', '\n'),  # Handle escaped newlines
                "client_email": google_client_email,
                "client_id": google_client_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{google_client_email}"
            }

            credentials = service_account.Credentials.from_service_account_info(creds_info)
            print("Successfully loaded Google Cloud credentials from individual environment variables")
            return credentials
        except Exception as e:
            print(f"Error creating credentials from individual environment variables: {e}")

    # Fallback to local file if running locally
    local_credentials_path = "collectorsage.json"
    if os.path.exists(local_credentials_path):
        print("Using local credentials file for development")
        return service_account.Credentials.from_service_account_file(local_credentials_path)

    print("No Google Cloud credentials found. Please set GOOGLE_CREDENTIALS_JSON environment variable or individual credential environment variables.")
    return None

def get_vision_client():
    """Get Google Vision client with fresh credentials"""
    credentials = get_google_credentials()
    if credentials:
        return vision.ImageAnnotatorClient(credentials=credentials)
    else:
        # Try to initialize with default credentials (for cloud environments)
        try:
            return vision.ImageAnnotatorClient()
        except Exception as e:
            print(f"Failed to initialize Google Vision client: {e}")
            return None

def recognize_comic_issue_with_google_vision(image_path):
    vision_client = get_vision_client()
    if not vision_client:
        print("Google Vision client not available. Skipping text recognition.")
        print("This could be due to missing Google Cloud credentials.")
        return None

    try:
        print(f"Attempting to read image file: {image_path}")
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        print(f"Successfully read image file, size: {len(content)} bytes")

        image = vision.Image(content=content)
        print("Calling Google Vision API for text detection...")
        response = vision_client.text_detection(image=image)

        # Check for API errors
        if response.error.message:
            print(f"Google Vision API error: {response.error.message}")
            return None

        texts = response.text_annotations

        if texts:
            recognized_text = texts[0].description
            print(f"Recognized text: {recognized_text}")
            return recognized_text
        else:
            print("No text recognized in the image.")
            return None
    except Exception as e:
        print(f"Error during Google Vision text recognition: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return None

def convert_image_to_jpg(image_path, max_size=(1024, 1024), quality=85):
    """Convert and optimize image for faster processing"""
    with open(image_path, 'rb') as image_file:
        image = Image.open(image_file)

        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize if image is too large (speeds up API calls)
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            print(f"Resized image from original to {image.size} for faster processing")

        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=quality, optimize=True)
        return buffered.getvalue()

def get_comic_details_with_claude_optimized(image_path):
    """Optimized version that gets comic details faster with better prompting"""
    try:
        start_time = time.time()
        print("Converting and optimizing image for Claude API...")

        # Use optimized image conversion
        base64_image = base64.b64encode(convert_image_to_jpg(image_path, max_size=(800, 800), quality=80)).decode('utf-8')
        print(f"Optimized image converted to base64, length: {len(base64_image)}")

        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_api_key:
            print("Error: ANTHROPIC_API_KEY environment variable not set")
            return None

        print("Calling Claude API for comic details extraction...")
        client = anthropic.Client(api_key=anthropic_api_key)

        # Optimized prompt for faster, more accurate extraction
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=512,  # Reduced tokens for faster response
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": (
                                "Extract comic book information from this image. Look for the title, issue number, and year.\n\n"
                                "Respond ONLY in this exact format:\n"
                                "Title: [comic title]\n"
                                "Issue Number: [number only, or 'N/A' if not visible]\n"
                                "Year: [4-digit year, or 'N/A' if not visible]\n\n"
                                "Be concise and accurate."
                            )
                        }
                    ]
                }
            ]
        )

        processing_time = time.time() - start_time
        print(f"Claude API call completed in {processing_time:.2f} seconds")

        if response and response.content:
            text_blocks = [block.text for block in response.content if block.type == 'text']
            text_response = ''.join(text_blocks)
            print(f"Claude API response: {text_response}")
            details = parse_comic_details(text_response)
            print(f"Parsed comic details: {details}")
            return details
        else:
            print("Error: No content in Claude API response")
            return None
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return None

def get_comic_details_with_claude(image_path):
    """Legacy version - keeping for compatibility"""
    return get_comic_details_with_claude_optimized(image_path)

def parse_comic_details(text):
    details = {}
    for line in text.split('\n'):
        if line.startswith("Title: "):
            details['title'] = line.replace("Title: ", "").strip()
        elif line.startswith("Issue Number: "):
            details['issue_number'] = line.replace("Issue Number: ", "").strip()
        elif line.startswith("Volume: "):
            details['volume'] = line.replace("Volume: ", "").strip()
        elif line.startswith("Year: "):
            details['year'] = line.replace("Year: ", "").strip()
    return details

def process_comic_image_fast(image_path):
    """Fast processing - skip Google Vision, go directly to Claude"""
    print("Fast processing comic image...")
    start_time = time.time()

    # Skip Google Vision entirely and go straight to Claude
    print("Getting comic details directly with Claude (skipping Google Vision)...")
    comic_details = get_comic_details_with_claude_optimized(image_path)

    if comic_details:
        print(f"Comic details recognized: {comic_details}")

        # Extract and clean up title
        title = comic_details.get('title', '').strip()
        if not title or title.lower() in ['n/a', 'unknown', '']:
            title = "Unknown Title"

        # Handle issue number
        issue_number = comic_details.get('issue_number', '').strip()
        if not issue_number or issue_number.lower() in ['n/a', 'not specified', 'unknown']:
            issue_number = ''

        # Extract year, if present - be more flexible
        year = comic_details.get('year', '').strip()
        if year and year.lower() not in ['n/a', 'unknown', '']:
            # Look for any 4-digit year in the response
            year_match = re.search(r'(19|20)\d{2}', year)
            if year_match:
                year = year_match.group()
                print(f"Extracted year from Claude response: {year}")
            else:
                year = ''
        else:
            year = ''

        # Prepare search query
        search_terms = [title]
        if issue_number:
            search_terms.append(issue_number)
        if year:
            search_terms.append(year)

        search_query = " ".join(search_terms).strip()

        # Prepare comic details for return
        cleaned_details = {
            'title': title,
            'issue_number': issue_number if issue_number else 'N/A',
            'volume': comic_details.get('volume', 'N/A'),
            'year': year if year else 'N/A'
        }

        processing_time = time.time() - start_time
        print(f"Fast processing completed in {processing_time:.2f} seconds")
        print(f"Search query: {search_query}")
        return cleaned_details, search_query
    else:
        print("No comic details recognized.")
        return None, None

def process_comic_image(image_path):
    """Main processing function - now uses fast processing by default"""
    return process_comic_image_fast(image_path)

def process_comic_image_legacy(image_path):
    """Legacy processing with Google Vision + Claude (slower but more thorough)"""
    print("Processing comic image with legacy method...")
    recognized_text = recognize_comic_issue_with_google_vision(image_path)

    if recognized_text:
        print("Getting comic details with Claude...")
        comic_details = get_comic_details_with_claude(image_path)
        if comic_details:
            print(f"Comic details recognized: {comic_details}")

            # Extract and clean up title
            title = comic_details.get('title', '').strip()
            if not title:
                title = "Unknown Title"

            # Handle issue number
            issue_number = comic_details.get('issue_number', '').strip()
            if not issue_number or 'not specified' in issue_number.lower():
                issue_number = ''

            # Extract year, if present - be more flexible
            year = comic_details.get('year', '').strip()
            if year and year.lower() not in ['n/a', 'unknown', '']:
                # Look for any 4-digit year in the response
                year_match = re.search(r'(19|20)\d{2}', year)
                if year_match:
                    year = year_match.group()
                    print(f"Extracted year from Claude response: {year}")
                else:
                    year = ''
            else:
                year = ''

            # Prepare search query
            search_terms = [title]
            if issue_number:
                search_terms.append(issue_number)
            if year:
                search_terms.append(year)

            search_query = " ".join(search_terms).strip()

            # Prepare comic details for return
            cleaned_details = {
                'title': title,
                'issue_number': issue_number if issue_number else 'N/A',
                'volume': comic_details.get('volume', 'N/A'),
                'year': year if year else 'N/A'
            }

            print(f"Fetching eBay data for query: {search_query}")
            return cleaned_details, search_query
        else:
            print("No comic details recognized.")
            return None, None
    else:
        print("No text recognized in the image.")
        return None, None

# Example usage
if __name__ == "__main__":
    image_path = "path_to_your_image.jpg"
    result, search_query = process_comic_image(image_path)
    if result:
        print(f"Comic details: {result}")
        print(f"Search query: {search_query}")
    else:
        print("Failed to process image or extract comic details.")

# Example usage
if __name__ == "__main__":
    image_path = "path_to_your_image.jpg"
    result, search_query = process_comic_image(image_path)
    if result:
        print(f"Comic details: {result}")
        print(f"Search query: {search_query}")
