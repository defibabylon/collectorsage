import os
import json
import logging
from sentence_transformers import SentenceTransformer
from unidecode import unidecode
from tqdm import tqdm
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import re

# Setup logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s [%(levelname)s] %(message)s', 
                    handlers=[logging.FileHandler("upload_vectors.log"), 
                              logging.StreamHandler()])

# Load environment variables
load_dotenv()

# Initialize Pinecone
api_key = os.getenv('PINECONE_API_KEY')
index_name = os.getenv('PINECONE_INDEX_NAME')
environment = os.getenv('PINECONE_ENVIRONMENT')

# Create an instance of Pinecone
pc = Pinecone(api_key=api_key)

# Check if the index exists
if index_name in pc.list_indexes().names():
    pc.delete_index(index_name)

pc.create_index(
    name=index_name,
    dimension=384,
    metric='cosine',
    spec=ServerlessSpec(cloud='aws', region='us-east-1')
)
index = pc.Index(index_name)
logging.info(f"Pinecone index '{index_name}' created successfully.")

# Load pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')
logging.info("Model loaded successfully.")

def parse_comic_entry(entry):
    title = entry.get('title', '')
    match = re.match(r"(.*?):? (.*?) \((\d{4})\) By (.*?) Volume (\d+),(\d+)(.*?)(?:\s*\(.*?\))?", title)
    if not match:
        logging.warning(f"Unable to parse title: {title}")
        return None
    
    comic_title, series, year, publisher, volume, issue_number, condition = match.groups()
    
    # Extract price from the entry
    price_str = entry.get('html', '')
    price = 0.0
    price_match = re.search(r'£(\d+(?:\.\d{2})?)', price_str)
    if price_match:
        try:
            price = float(price_match.group(1))
        except ValueError:
            logging.warning(f"Unable to convert price to float: {price_match.group(1)}")
    else:
        price_match = re.search(r'\b(\d+(?:\.\d{2})?)\b', price_str)
        if price_match:
            try:
                price = float(price_match.group(1))
            except ValueError:
                logging.warning(f"Unable to convert price to float: {price_match.group(1)}")
        else:
            logging.warning(f"Unable to extract price from: {price_str}")

    return {
        "title": comic_title.strip(),
        "series": series.strip() if series else "",
        "year": int(year),
        "publisher": publisher.strip(),
        "volume": int(volume),
        "issue_number": int(issue_number),
        "condition": condition.strip(),
        "price": price,
        "url": entry.get('url', ''),
        "full_title": title  # Keep the full title for reference
    }

# Utility function to read and validate JSON data
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error reading JSON file {file_path}: {e}")
        return None

# Load JSON files
db_path = r"D:\projects\2024\Q3\collectorsage\databases"
json_files = [os.path.join(db_path, f) for f in os.listdir(db_path) if f.endswith('.json')]
logging.info(f"Found {len(json_files)} JSON files in the database directory.")

# Process each JSON file
batch_size = 50
for json_file in tqdm(json_files, desc="Processing JSON files"):
    comic_data = load_json(json_file)
    if not comic_data:
        continue

    batch = []
    for comic in tqdm(comic_data, desc=f"Uploading Vectors from {json_file}", leave=False):
        parsed_comic = parse_comic_entry(comic)
        if not parsed_comic:
            continue

        vector = model.encode(parsed_comic['full_title'])
        
        # Create a unique ID
        comic_id = f"{parsed_comic['title']}_{parsed_comic['issue_number']}_{parsed_comic['year']}"
        comic_id = unidecode(comic_id)  # Remove any non-ASCII characters

        batch.append({"id": comic_id, "values": vector.tolist(), "metadata": parsed_comic})
        
        if len(batch) >= batch_size:
            try:
                response = index.upsert(vectors=batch)
                logging.debug(f"Upsert response: {response}")
            except Exception as e:
                logging.error(f"Error upserting batch: {e}")
            batch = []

    if batch:
        try:
            response = index.upsert(vectors=batch)
            logging.debug(f"Final batch upsert response: {response}")
        except Exception as e:
            logging.error(f"Error upserting final batch: {e}")

# Confirm all vectors are uploaded
logging.info("Checking index status...")
index_stats = index.describe_index_stats()
logging.info(f"Index contains {index_stats['total_vector_count']} vectors.")
logging.info("All vectors uploaded successfully.")
