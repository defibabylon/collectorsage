import anthropic
import base64
import os
import re
import json
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image
import io

# Initialize Google Vision client
def get_google_credentials():
    """Get Google Cloud credentials from environment variables or file."""
    # First, try to use GOOGLE_APPLICATION_CREDENTIALS if it's set
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        return None  # Let the client use default credentials

    # If not, try to use GOOGLE_CREDENTIALS_JSON environment variable
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
            print("Successfully loaded Google Cloud credentials from environment variable")
            return credentials
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing GOOGLE_CREDENTIALS_JSON: {e}")
            print(f"First 100 characters of credentials: {google_creds_json[:100]}...")
            return None

    # Fallback to local file if running locally
    local_credentials_path = "D:\\projects\\2024\\Q3\\collectorsage\\collectorsage-eec946bf70cd.json"
    if os.path.exists(local_credentials_path):
        return service_account.Credentials.from_service_account_file(local_credentials_path)

    print("No Google Cloud credentials found. Please set GOOGLE_CREDENTIALS_JSON environment variable.")
    return None

# Get credentials and initialize client
credentials = get_google_credentials()
if credentials:
    vision_client = vision.ImageAnnotatorClient(credentials=credentials)
else:
    # Try to initialize with default credentials (for cloud environments)
    try:
        vision_client = vision.ImageAnnotatorClient()
    except Exception as e:
        print(f"Failed to initialize Google Vision client: {e}")
        vision_client = None

def recognize_comic_issue_with_google_vision(image_path):
    if not vision_client:
        print("Google Vision client not available. Skipping text recognition.")
        return None

    try:
        with open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = vision_client.text_detection(image=image)
        texts = response.text_annotations

        if texts:
            recognized_text = texts[0].description
            print(f"Recognized text: {recognized_text}")
            return recognized_text
        else:
            print("No text recognized.")
            return None
    except Exception as e:
        print(f"Error during Google Vision text recognition: {e}")
        return None

def convert_image_to_jpg(image_path):
    with open(image_path, 'rb') as image_file:
        image = Image.open(image_file)
        image = image.convert('RGB')
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        return buffered.getvalue()

def get_comic_details_with_claude(image_path):
    base64_image = base64.b64encode(convert_image_to_jpg(image_path)).decode('utf-8')

    client = anthropic.Client(api_key=os.getenv('ANTHROPIC_API_KEY'))
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
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
                            "Given the following image, provide the title, issue number, volume, and publication year of the comic book.\n\n"
                            "Provide the information in the following format:\n"
                            "Title: <Title>\n"
                            "Issue Number: <Issue Number>\n"
                            "Volume: <Volume>\n"
                            "Year: <Year>"
                        )
                    }
                ]
            }
        ]
    )

    if response and response.content:
        text_blocks = [block.text for block in response.content if block.type == 'text']
        text_response = ''.join(text_blocks)
        details = parse_comic_details(text_response)
        return details
    else:
        print("Error recognizing comic issue with Claude.")
        return None

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

def process_comic_image(image_path):
    print("Processing comic image...")
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
            
            # Extract year, if present
            year = comic_details.get('year', '').strip()
            year_match = re.search(r'\d{4}', year)
            if year_match:
                year = year_match.group()
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
