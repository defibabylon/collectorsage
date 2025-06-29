import logging
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os
import json
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
from jellyfish import soundex
import re

# Setup logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s [%(levelname)s] %(message)s')

# Load environment variables
load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))

# Load the pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load DC Fandom databases
def load_dc_fandom_databases():
    """Load DC Fandom databases for additional metadata."""
    dc_fandom_data = []
    database_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'databases')

    try:
        # Load DC-Fandom-1.json
        dc_fandom_1_path = os.path.join(database_path, 'DC-Fandom-1.json')
        if os.path.exists(dc_fandom_1_path):
            with open(dc_fandom_1_path, 'r', encoding='utf-8') as f:
                dc_fandom_1 = json.load(f)
                dc_fandom_data.extend(dc_fandom_1)
                logging.info(f"Loaded {len(dc_fandom_1)} entries from DC-Fandom-1.json")

        # Load DC-Fandom-2.json
        dc_fandom_2_path = os.path.join(database_path, 'DC-Fandom-2.json')
        if os.path.exists(dc_fandom_2_path):
            with open(dc_fandom_2_path, 'r', encoding='utf-8') as f:
                dc_fandom_2 = json.load(f)
                dc_fandom_data.extend(dc_fandom_2)
                logging.info(f"Loaded {len(dc_fandom_2)} entries from DC-Fandom-2.json")

    except Exception as e:
        logging.warning(f"Error loading DC Fandom databases: {e}")

    return dc_fandom_data

# Initialize DC Fandom data
dc_fandom_data = load_dc_fandom_databases()

def preprocess_title(title):
    """Preprocess the title to improve matching."""
    # Convert to lowercase
    title = title.lower()
    # Remove common words that might interfere with matching
    common_words = ['the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for', 'by']
    title_words = title.split()
    title = ' '.join([word for word in title_words if word not in common_words])
    # Remove any non-alphanumeric characters
    title = re.sub(r'[^\w\s]', '', title)
    return title

def calculate_title_similarity(stored_title, search_title):
    """Calculate the similarity between two titles using multiple methods."""
    stored_title = preprocess_title(stored_title)
    search_title = preprocess_title(search_title)
    
    ratio = fuzz.ratio(stored_title, search_title)
    partial_ratio = fuzz.partial_ratio(stored_title, search_title)
    token_sort_ratio = fuzz.token_sort_ratio(stored_title, search_title)
    token_set_ratio = fuzz.token_set_ratio(stored_title, search_title)
    
    soundex_match = 100 if soundex(stored_title) == soundex(search_title) else 0
    
    # Weighted average of different similarity measures
    similarity = (ratio * 0.3 + partial_ratio * 0.2 + token_sort_ratio * 0.2 + 
                  token_set_ratio * 0.2 + soundex_match * 0.1)
    
    return similarity

def compare_issue_numbers(stored_issue, search_issue):
    """Compare issue numbers, handling various formats."""
    try:
        stored_issue = float(re.sub(r'\.0$', '', str(stored_issue)))
        search_issue = float(re.sub(r'\.0$', '', str(search_issue)))
        return abs(stored_issue - search_issue) < 0.1
    except ValueError:
        # If conversion to float fails, do a string comparison
        return str(stored_issue).strip() == str(search_issue).strip()

def search_dc_fandom_metadata(title):
    """Search DC Fandom databases for additional character/series metadata."""
    metadata_results = []

    if not dc_fandom_data:
        return metadata_results

    title_lower = title.lower()

    for entry in dc_fandom_data:
        entry_title = entry.get('title', '').lower()

        # Check if the comic title appears in the DC Fandom entry title
        if title_lower in entry_title or any(word in entry_title for word in title_lower.split() if len(word) > 3):
            # Extract relevant metadata from the entry
            metadata = {
                'source': 'DC Fandom',
                'title': entry.get('title', ''),
                'url': entry.get('url', ''),
                'type': 'character_info'
            }

            # Try to extract additional info from the HTML content
            html_content = entry.get('html', '')
            if html_content:
                # Look for publisher info
                if 'DC' in html_content or 'DC Comics' in html_content:
                    metadata['publisher'] = 'DC Comics'

                # Look for character names or series info
                if 'Batman' in html_content:
                    metadata['character'] = 'Batman'
                elif 'Superman' in html_content:
                    metadata['character'] = 'Superman'
                elif 'Wonder Woman' in html_content:
                    metadata['character'] = 'Wonder Woman'
                elif 'Flash' in html_content:
                    metadata['character'] = 'Flash'
                elif 'Green Lantern' in html_content:
                    metadata['character'] = 'Green Lantern'
                elif 'Aquaman' in html_content:
                    metadata['character'] = 'Aquaman'

            metadata_results.append(metadata)

            # Limit to top 3 results to avoid overwhelming the response
            if len(metadata_results) >= 3:
                break

    return metadata_results

def fetch_database_info(title, issue_number):
    """Fetch both prices and metadata for a given comic book."""
    query_vector = model.encode(f"{title}").tolist()
    result = index.query(vector=query_vector, top_k=20, include_metadata=True)

    logging.info(f"Query result for '{title}' issue '{issue_number}': {result}")

    matches = []
    for match in result['matches']:
        metadata = match['metadata']
        stored_title = metadata.get('series', '')
        stored_issue = metadata.get('issue_number', '')

        # Calculate title similarity
        title_similarity = calculate_title_similarity(stored_title, title)

        # Check issue number match
        issue_match = compare_issue_numbers(stored_issue, issue_number)

        # Calculate overall score
        overall_score = title_similarity + (50 if issue_match else 0)

        matches.append({
            'metadata': metadata,
            'score': overall_score
        })

    # Sort matches by score in descending order
    matches.sort(key=lambda x: x['score'], reverse=True)

    # Return the top 5 matches
    top_matches = matches[:5]

    prices = [float(match['metadata'].get('price', 0)) for match in top_matches if match['metadata'].get('price')]
    metadata = [match['metadata'] for match in top_matches]

    # Add DC Fandom metadata for additional context
    dc_fandom_metadata = search_dc_fandom_metadata(title)
    if dc_fandom_metadata:
        metadata.extend(dc_fandom_metadata)
        logging.info(f"Added {len(dc_fandom_metadata)} DC Fandom metadata entries")

    logging.debug(f"Top matches: {top_matches}")
    logging.debug(f"Fetched prices: {prices}")
    logging.debug(f"Total metadata entries: {len(metadata)}")

    return prices, metadata

def search_comics(query, top_k=5):
    logging.info(f"Searching for comics with query: {query}")
    query_vector = model.encode(query).tolist()
    
    result = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )
    
    logging.info(f"Search result: {result}")
    
    results = []
    for match in result['matches']:
        metadata = match['metadata']
        results.append({
            "score": match['score'],
            "title": metadata.get('full_title', metadata.get('title', 'Unknown')),
            "issue_number": metadata.get('issue_number', 'Unknown'),
            "price": metadata.get('price', 'Unknown'),
            "publisher": metadata.get('publisher', 'Unknown'),
            "year": metadata.get('year', 'Unknown'),
            "condition": metadata.get('condition', 'Unknown'),
            "url": metadata.get('url', 'Unknown')
        })
    return results

# Test function
def test_database_queries():
    title = "The Outlaw Kid"
    issue_numbers = ["9", "9.0", 9, 9.0]
    
    for issue_number in issue_numbers:
        print(f"\nTesting fetch_database_info for '{title}' issue '{issue_number}':")
        prices, metadata = fetch_database_info(title, issue_number)
        print(f"Prices found: {prices}")
        print(f"Metadata found: {metadata}")
    
    print("\nTesting search_comics:")
    results = search_comics(title)
    for result in results:
        print(f"Score: {result['score']}")
        print(f"Title: {result['title']}")
        print(f"Issue Number: {result['issue_number']}")
        print(f"Price: {result['price']}")
        print(f"Publisher: {result['publisher']}")
        print(f"Year: {result['year']}")
        print(f"Condition: {result['condition']}")
        print(f"URL: {result['url']}")
        print("----")

if __name__ == "__main__":
    test_database_queries()