import logging
import os
import anthropic
from utils.currency_conversion import convert_currency
from utils.tips import generate_location_tips, generate_item_description

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s [%(levelname)s] %(message)s', 
                    handlers=[logging.FileHandler("app.log", encoding='utf-8'), 
                              logging.StreamHandler()])

def generate_qualitative_report(title, issue_number, year, avg_price, database_avg_price, ebay_data, client, sales_trend, metadata=None):
    logging.info("Generating qualitative report...")
    logging.debug(f"Input parameters: title={title}, issue_number={issue_number}, year={year}, avg_price={avg_price}, database_avg_price={database_avg_price}, sales_trend={sales_trend}")
    logging.debug(f"Received metadata: {metadata}")
    
    try:
        items = ebay_data.get('itemSummaries', [])
        total_listings = len(items)
        
        # Use eBay data for price ranges
        prices = [float(item['price']['value']) for item in items if 'price' in item]
        ebay_min_price = min(prices) if prices else 'Unknown'
        ebay_max_price = max(prices) if prices else 'Unknown'
        
        # Use metadata if available, otherwise use placeholders
        if metadata and isinstance(metadata, list) and metadata:
            meta = metadata[0]
            publisher = meta.get('publisher', 'Unknown')
            publication_year = meta.get('year', year)
            
            # Extract database price range
            database_prices = [float(m.get('price', 0)) for m in metadata if 'price' in m]
            db_min_price = min(database_prices) if database_prices else 'Unknown'
            db_max_price = max(database_prices) if database_prices else 'Unknown'
            if not database_avg_price:
                database_avg_price = sum(database_prices) / len(database_prices) if database_prices else 0
        else:
            publisher = "Unknown (Not found in database)"
            publication_year = year
            db_min_price = 'Unknown'
            db_max_price = 'Unknown'
            if not database_avg_price:
                database_avg_price = 0

        logging.debug(f"Processed data: publisher={publisher}, publication_year={publication_year}, db_min_price={db_min_price}, db_max_price={db_max_price}, database_avg_price={database_avg_price}")

        prompt = f"""
        You are an expert comic book dealer. Analyze the following information about "{title}" issue #{issue_number} ({year}) and write a detailed price report:

        Total eBay Listings: {total_listings}
        Average eBay Price: £{avg_price:.2f}
        eBay Price Range: £{ebay_min_price} - £{ebay_max_price}
        Database Price Range: £{db_min_price} - £{db_max_price}
        Database Average Price: £{database_avg_price:.2f}
        Publisher: {publisher}
        Publication Year: {publication_year}
        Recent Sales Trend: {sales_trend}

        Please provide a comprehensive report including:
        1. Overview of the comic's significance and collectible status
        2. Analysis of the current market prices, comparing eBay and Database prices
        3. Factors influencing the comic's value
        4. Advice for potential buyers or sellers
        5. A brief outline of the story (2-3 sentences)
        6. Any other relevant insights

        Use the following format for your report:
        [Comic book name, volume]
        Key Features: [Notable aspects]
        Impact: [1-5 stars]
        Rarity: [1-5 stars]
        Value: [1-5 stars]
        Story: [1-5 stars]
        Artwork: [1-5 stars]
        Story Outline: [2-3 sentence summary of the comic's story]
        [Your detailed analysis and insights]
        """

        logging.debug(f"Prompt for Claude: {prompt}")

        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        logging.debug("Claude 3.5 Sonnet API Response: %s", response)

        if response and response.content:
            response_content = response.content[0].text if response.content else ""
            logging.debug("Extracted response content: %s", response_content)
            return response_content.strip()
        else:
            logging.error("No content in Claude API response")
            return "Error: No content in Claude API response"
    
    except Exception as e:
        logging.exception("Error generating qualitative report")
        return f"An error occurred while generating the report: {str(e)}"

# Example usage
if __name__ == "__main__":
    # Replace these with your actual parameters
    title = "The Outlaw Kid"
    issue_number = 9
    year = 1955
    avg_price = 43.96
    database_avg_price = 0.0
    ebay_data = {"itemSummaries": [{"price": {"value": "12.84"}}, {"price": {"value": "1130.0"}}]}
    sales_trend = "Stable"
    metadata = [{'publisher': 'Atlas', 'year': 1955, 'price': 199.95}]
    
    client = anthropic.Client(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    report = generate_qualitative_report(title, issue_number, year, avg_price, database_avg_price, ebay_data, client, sales_trend, metadata)
    print(report)
