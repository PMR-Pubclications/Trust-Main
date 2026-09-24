import time
import logging
import json
import os
from requests.exceptions import RequestException

# Configure logging to write to standard output and a log file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("agent_portfolio.log"),
        logging.StreamHandler()
    ]
)

class OpenSeaAgentClient:
    def __init__(self, api_key: str, scoped_token: str, base_url: str = "https://api.opensea.io"):
        self.api_key = api_key
        self.scoped_token = scoped_token
        self.base_url = base_url
        self.headers = {
            "X-API-KEY": self.api_key,
            "Authorization": f"Bearer {self.scoped_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_nfts(self, chain: str, address: str, limit: int = 50):
        url = f"{self.base_url}/api/v2/chain/{chain}/account/{address}/nfts"
        params = {"limit": limit}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

def run_agent_loop(interval_seconds: int = 300):
    """
    Runs a continuous background loop to monitor wallet assets.
    Default interval is set to 300 seconds (5 minutes).
    """
    # Load credentials safely from environment variables
    api_key = os.getenv("OPENSEA_API_KEY", "YOUR_API_KEY")
    scoped_token = os.getenv("OPENSEA_SCOPED_TOKEN", "YOUR_SCOPED_AGENT_TOKEN")
    admin_wallet = os.getenv("ADMIN_WALLET_ADDRESS", "0xYOUR_ADMIN_WALLET_ADDRESS")
    
    client = OpenSeaAgentClient(api_key=api_key, scoped_token=scoped_token)
    
    logging.info(f"Starting headless OpenSea agent monitor for wallet: {admin_wallet}")
    
    while True:
        try:
            logging.info("Fetching latest wallet assets...")
            nfts_data = client.get_nfts(chain="ethereum", address=admin_wallet, limit=20)
            
            nft_count = len(nfts_data.get("nfts", []))
            logging.info(f"Successfully checked holdings. Total tracked NFTs found: {nft_count}")
            
            # Here you can inject your custom decision logic:
            # e.g., evaluate floor prices, check triggers, or execute automated actions.

        except RequestException as e:
            logging.error(f"API request failed: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in agent loop: {e}")
            
        logging.info(f"Sleeping for {interval_seconds} seconds...\n")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    import requests
    # Run the loop every 5 minutes (300 seconds)
    run_agent_loop(interval_seconds=300)
