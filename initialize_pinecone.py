import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load environment variables from a specific path
load_dotenv(dotenv_path='.env')

# Retrieve environment variables
api_key = os.getenv('PINECONE_API_KEY')
environment = os.getenv('PINECONE_ENVIRONMENT')
index_name = os.getenv('PINECONE_INDEX_NAME')

# Check if environment variables are loaded correctly
if not api_key or not environment or not index_name:
    raise ValueError("Missing one or more environment variables: PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME")

# Create an instance of the Pinecone class
pc = Pinecone(api_key=api_key)

# Create a new index if it doesn't exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # Dimension for text-embedding-ada-002
        metric="cosine",  # Metric for text-embedding-ada-002
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    print(f"Index '{index_name}' created successfully.")
else:
    print(f"Index '{index_name}' already exists.")