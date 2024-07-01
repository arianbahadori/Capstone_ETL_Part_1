# -*- coding: utf-8 -*-
"""Welcome to Colaboratory
Automatically generated by Colab.
"""

# Libraries
import psycopg2 as psql
import json
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
import requests

# Database connection parameters
password = os.getenv('sql_password')
user = os.getenv('user')
my_host = os.getenv('host')

conn = psql.connect(database="pagila",
                    user=user,
                    host=my_host,
                    password=password,
                    port=5432)
cur = conn.cursor()

# Define the API URLs and API key
latest_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
meta_data_url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/info"
api_key = os.getenv('api_key')

# Headers for the API request
headers = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": api_key
}

# Parameters for the API requests
params_latest = {
    'start': '1',
    'limit': '100',
    'convert': 'USD'
}

# Function to get the latest data
def get_latest_data():
    response = requests.get(latest_url, params=params_latest, headers=headers)
    return response.json()

# Function to get cryptocurrency info (including logos and descriptions)
def get_meta_data(crypto_ids):
    params_meta = {
        'id': ','.join(map(str, crypto_ids))
    }
    response = requests.get(meta_data_url, params=params_meta, headers=headers)
    return response.json()

# Fetch data from the APIs
latest_data = get_latest_data()

# Extract and sort the crypto IDs by cmc_rank
sorted_data = sorted(latest_data['data'], key=lambda x: x['cmc_rank'])
crypto_ids = [crypto['id'] for crypto in sorted_data]

# Fetch meta data using the extracted crypto IDs
meta_data = get_meta_data(crypto_ids)

# Insert sorted latest data into the database
for crypto in sorted_data:
    crypto_id = crypto['id']
    name = crypto['name']
    symbol = crypto['symbol']
    cmc_rank = crypto['cmc_rank']
    circulating_supply = crypto['circulating_supply']
    date_added = datetime.strptime(crypto['date_added'], "%Y-%m-%dT%H:%M:%S.%fZ")

    quote = crypto['quote']['USD']
    price_usd = quote['price']
    volume_24h_usd = quote['volume_24h']
    percent_change_1h_usd = quote['percent_change_1h']
    percent_change_24h_usd = quote['percent_change_24h']
    percent_change_7d_usd = quote['percent_change_7d']
    market_cap_usd = quote['market_cap']
    market_cap_dominance_usd = quote['market_cap_dominance']

    # Fetch logo and description from meta_data
    logo_url = meta_data['data'][str(crypto_id)]['logo']
    description = meta_data['data'][str(crypto_id)]['description']

    # Build the INSERT statement for the latest data
    insert_latest_query = """
    INSERT INTO student.de10_arba_test (
        crypto_id, name, symbol, cmc_rank, circulating_supply, date_added,
        price_usd, volume_24h_usd, percent_change_1h_usd,
        percent_change_24h_usd, percent_change_7d_usd, market_cap_usd, market_cap_dominance_usd,
        logo_url, description
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (crypto_id) DO UPDATE SET
        name = EXCLUDED.name,
        symbol = EXCLUDED.symbol,
        cmc_rank = EXCLUDED.cmc_rank,
        circulating_supply = EXCLUDED.circulating_supply,
        date_added = EXCLUDED.date_added,
        price_usd = EXCLUDED.price_usd,
        volume_24h_usd = EXCLUDED.volume_24h_usd,
        percent_change_1h_usd = EXCLUDED.percent_change_1h_usd,
        percent_change_24h_usd = EXCLUDED.percent_change_24h_usd,
        percent_change_7d_usd = EXCLUDED.percent_change_7d_usd,
        market_cap_usd = EXCLUDED.market_cap_usd,
        market_cap_dominance_usd = EXCLUDED.market_cap_dominance_usd,
        logo_url = EXCLUDED.logo_url,
        description = EXCLUDED.description;
    """

    # Execute the INSERT statement for the latest data
    cur.execute(insert_latest_query, (
        crypto_id, name, symbol, cmc_rank, circulating_supply, date_added,
        price_usd, volume_24h_usd, percent_change_1h_usd,
        percent_change_24h_usd, percent_change_7d_usd, market_cap_usd, market_cap_dominance_usd,
        logo_url, description
    ))

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
