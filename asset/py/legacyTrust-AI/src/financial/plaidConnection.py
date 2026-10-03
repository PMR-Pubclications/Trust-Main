import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

import plaid
from plaid.api import plaid_api
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.transfer_authorization_create_request import TransferAuthorizationCreateRequest
from plaid.model.transfer_create_request import TransferCreateRequest
from plaid.model.transfer_network import TransferNetwork
from plaid.model.transfer_type import TransferType
from plaid.model.ach_class import ACHClass
from plaid.model.transfer_user_in_request import TransferUserInRequest

logger = logging.getLogger("TrustPlatform.Plaid")

class PlaidTrustWrapper:
    """Core wrapper for trust bank accounts, liquidity monitoring, and ACH transfer execution."""

    def __init__(self, client_id: str, secret: str, env: str = "sandbox"):
        host = plaid.Environment.Sandbox if env.lower() == "sandbox" else plaid.Environment.Production
        configuration = plaid.Configuration(
            host=host,
            api_key={"clientId": client_id, "secret": secret, "plaidVersion": "2020-09-14"}
        )
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

    def get_account_balances(self, access_token: str) -> List[Dict[str, Any]]:
        """Fetch real-time available and ledger balances for trust depository accounts."""
        try:
            request = AccountsBalanceGetRequest(access_token=access_token)
            response = self.client.accounts_balance_get(request)
            accounts_data = []
            for acc in response.accounts:
                accounts_data.append({
                    "account_id": acc.account_id,
                    "name": acc.name,
                    "type": str(acc.type),
                    "subtype": str(acc.subtype),
                    "available_balance": float(acc.balances.available or 0.0),
                    "current_balance": float(acc.balances.current or 0.0),
                    "currency": acc.balances.iso_currency_code
                })
            return accounts_data
        except plaid.ApiException as e:
            logger.error(f"Plaid Balance Retrieval Error: {e}")
            raise RuntimeError(f"Plaid API Error: {e.body}")

    def sync_transactions(self, access_token: str, cursor: Optional[str] = None) -> Dict[str, Any]:
        """Incrementally sync settled and pending bank transactions for ledger reconciliation."""
        try:
            request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor or ""
            )
            response = self.client.transactions_sync(request)
            return {
                "added":Below is the core unified Python wrapper integrating Plaid (bank monitoring and transaction ingestion) and Alpaca (treasury execution and order placement) into the trust management platform.

### Dependencies

```bash
pip install plaid-python alpaca-py pydantic
