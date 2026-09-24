import requests
import json

class OpenSeaAgentClient:
    def __init__(self, api_key: str, scoped_token: str, base_url: str = "https://api.opensea.io"):
        """
        Initializes the OpenSea Agent Client with API keys and scoped tokens.
        """
        self.api_key = api_key
        self.scoped_token = scoped_token
        self.base_url = base_url
        self.headers = {
            "X-API-KEY": self.api_key,
            "Authorization": f"Bearer {self.scoped_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_portfolio(self, address: str):
        """Fetches total value, asset breakdown, and portfolio data for the admin wallet."""
        url = f"{self.base_url}/api/v2/account/{address}/portfolio"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_nfts(self, chain: str, address: str, limit: int = 50):
        """Inspects all NFTs owned by the account across a specified chain."""
        url = f"{self.base_url}/api/v2/chain/{chain}/account/{address}/nfts"
        params = {"limit": limit}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def sweep_collection(self, collection_slug: str, quantity: int, max_price: str, taker: str):
        """Autonomous buying: Sweeps up to N items from a collection floor."""
        url = f"{self.base_url}/api/v2/listings/sweep"
        payload = {
            "collection_slug": collection_slug,
            "quantity": quantity,
            "max_price": max_price,
            "taker": taker
        }
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()

    def create_listing(self, chain: str, contract_address: str, token_id: str, start_price: str, expiration_time: int, taker: str = "0x0000000000000000000000000000000000000000"):
        """Autonomous selling: Generates blockchain actions and payloads to list an NFT."""
        url = f"{self.base_url}/api/v2/listings/actions"
        payload = {
            "chain": chain,
            "asset_contract_address": contract_address,
            "token_id": token_id,
            "taker": taker,
            "start_price": start_price,
            "expiration_time": expiration_time
        }
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()

    def get_agent_relationships(self):
        """Verifies the agent's ownership and binding state to the admin wallet."""
        url = f"{self.base_url}/api/v2/accounts/agent-relationships"
        response = requests.get(url, headers=self.headers)
        return response.json()

# --- Example Usage ---
if __name__ == "__main__":
    # Replace these placeholder strings with your actual keys and addresses
    API_KEY = "YOUR_API_KEY"
    SCOPED_TOKEN = "YOUR_SCOPED_AGENT_TOKEN"
    ADMIN_WALLET = "0x26600142FC4B2ED0276536557fa8bF2a82F1d5c1"
    
    client = OpenSeaAgentClient(api_key=API_KEY, scoped_token=SCOPED_TOKEN)
    
    # 1. Verify agent relationship
    print("Verifying agent relationship...")
    print(client.get_agent_relationships())
    
    # 2. Check holdings
    print("Checking wallet NFTs on Ethereum...")
    nfts = client.get_nfts(chain="ethereum", address=ADMIN_WALLET, limit=10)
    print(json.dumps(nfts, indent=2))
