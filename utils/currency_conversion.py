import requests
import logging

def convert_currency(amount, from_currency, to_currency='GBP'):
    """
    Convert an amount from one currency to another using an external API.
    """
    logging.info(f"Converting currency from {from_currency} to {to_currency}...")
    try:
        response = requests.get(f'https://api.exchangerate-api.com/v4/latest/{from_currency}')
        response.raise_for_status()
        rates = response.json().get('rates', {})
        if to_currency in rates:
            return amount * rates[to_currency]
        else:
            logging.error(f"Currency not found: {to_currency}")
            return amount
    except requests.exceptions.RequestException as e:
        logging.exception(f"Error fetching exchange rates: {e}")
        return amount