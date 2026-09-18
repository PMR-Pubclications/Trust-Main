from datetime import datetime, timezone
import requests
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="Etherscan Date-Pull API Framework", version="1.0.0")

# Etherscan V2 Base URL (Supports 60+ EVM chains via chainid)
ETHERSCAN_V2_URL = "https://api.etherscan.io/v2/api"


class EtherscanDateFetcher:

  def __init__(self, api_key: str, chain_id: int = 1):
    self.api_key = api_key
    self.chain_id = chain_id  # 1 for Ethereum Mainnet, 42161 for Arbitrum, etc.

  def _date_to_timestamp(self, date_str: str, end_of_day: bool = False) -> int:
    """Converts a 'YYYY-MM-DD' string into a UTC Unix timestamp."""
    try:
      dt = datetime.strptime(date_str, "%Y-%m-%d")
      if end_of_day:
        dt = dt.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
      else:
        dt = dt.replace(hour=0, minute=0, second=0, tzinfo=timezone.utc)
      return int(dt.timestamp())
    except ValueError:
      raise HTTPException(
          status_code=400,
          detail="Invalid date format. Use YYYY-MM-DD (e.g., 2026-01-01).",
      )

  def get_block_by_timestamp(self, timestamp: int, closest: str = "before") -> int:
    """Maps a Unix timestamp to the closest block number using Etherscan API."""
    params = {
        "chainid": self.chain_id,
        "module": "block",
        "action": "getblocknobytime",
        "timestamp": timestamp,
        "closest": closest,
        "apikey": self.api_key,
    }

    response = requests.get(ETHERSCAN_V2_URL, params=params)
    data = response.json()

    if data.get("status") != "1":
      raise HTTPException(
          status_code=400,
          detail=f"Etherscan Block Lookup Error: {data.get('message', 'Unknown')}",
      )

    return int(data["result"])

  def pull_transactions_by_date(
      self, address: str, start_date: str, end_date: str
  ):
    """Resolves date range into block bounds and pulls normal transactions."""
    start_ts = self._date_to_timestamp(start_date, end_of_day=False)
    end_ts = self._date_to_timestamp(end_date, end_of_day=True)

    # Resolve date bounds to blockchain blocks
    start_block = self.get_block_by_timestamp(start_ts, closest="after")
    end_block = self.get_block_by_timestamp(end_ts, closest="before")

    if start_block > end_block:
      raise HTTPException(
          status_code=400,
          detail="Start block is greater than end block. Check date range.",
      )

    # Query transaction list endpoint using resolved blocks
    params = {
        "chainid": self.chain_id,
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": start_block,
        "endblock": end_block,
        "sort": "asc",
        "apikey": self.api_key,
    }

    response = requests.get(ETHERSCAN_V2_URL, params=params)
    data = response.json()

    if data.get("status") != "1" and data.get("message") != "No transactions found":
      raise HTTPException(
          status_code=400,
          detail=f"Etherscan Data API Error: {data.get('result')}",
      )

    return {
        "address": address,
        "start_date": start_date,
        "end_date": end_date,
        "resolved_start_block": start_block,
        "resolved_end_block": end_block,
        "transactions": data.get("result", []),
    }


# Initialize wrapper (Use environment variables for production keys)
# fetcher = EtherscanDateFetcher(api_key="NZWP67D6AMHG6HBH63W6HVZCCHCFUDUH99", chain_id=1)


@app.get("/api/v1/pull-txs-by-date")
def pull_txs_endpoint(
    address: str = Query(..., description="Target EVM wallet address"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    chain_id: int = Query(1, description="EVM Chain ID (default: 1 for Ethereum)"),
):
  """API Endpoint to pull transaction records over a specific date range."""
  # Dynamically initialize or pass credentials safely
  api_key = "YOUR_ETHERSCAN_API_KEY"
  fetcher = EtherscanDateFetcher(api_key=api_key, chain_id=chain_id)

  result = fetcher.pull_transactions_by_date(address, start_date, end_date)
  return {"status": "success", "data": result}
