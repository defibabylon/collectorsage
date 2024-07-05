import logging
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os
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
    
    logging.debug(f"Top matches: {top_matches}")
    logging.debug(f"Fetched prices: {prices}")
    
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