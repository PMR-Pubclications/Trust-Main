import requests
import json
import urllib3

# Disable self-signed cert warnings for local Docker LND REST proxy
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration parameters
LND_REST_HOST = "https://localhost:8080"
MACAROON_PATH = "admin.macaroon" # Ensure you map or mount your macaroon for auth
DESTINATION_ADDRESS = "3QnhndxFC1jYsuhHN5mG1nfq9h123daS4h"
SWEEP_THRESHOLD_SATS = 50000  # Minimum satoshis before triggering an on-chain sweep

def get_node_balance():
    url = f"{LND_REST_HOST}/v1/balance/channels"
    # In production, pass the macaroon header: {'Grpc-Metadata-Macaroon': macaroon_hex}
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        data = response.json()
        return int(data.get("balance", 0))
    else:
        print(f"Error fetching balance: {response.text}")
        return 0

def execute_on_chain_sweep(amount_sats):
    url = f"{LND_REST_HOST}/v1/transactions"
    payload = {
        "addr": DESTINATION_ADDRESS,
        "amt": amount_sats,
        "target_conf": 6 # Standard priority confirmation target
    }
    response = requests.post(url, json=payload, verify=False)
    if response.status_code == 200:
        print(f"Successfully swept {amount_sats} sats to Ellipal wallet!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Sweep failed: {response.text}")

if __name__ == "__main__":
    print("Checking LND node balances for automated clearing...")
    current_balance = get_node_balance()
    print(f"Current available balance: {current_balance} sats")
    
    if current_balance >= SWEEP_THRESHOLD_SATS:
        print(f"Threshold reached! Initiating sweep to {DESTINATION_ADDRESS}...")
        # Leave a small buffer for network transaction fees if sweeping 'all'
        sweep_amount = current_balance - 1000 
        if sweep_amount > 0:
            execute_on_chain_sweep(sweep_amount)
    else:
        print(f"Threshold of {SWEEP_THRESHOLD_SATS} sats not yet met. Standing by.")
