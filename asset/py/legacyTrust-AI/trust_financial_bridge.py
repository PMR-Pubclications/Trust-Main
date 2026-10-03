import os
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field

# --- Plaid Imports ---
import plaid
from plaid.api import plaid_api
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.processor_token_create_request import ProcessorTokenCreateRequest

# --- Alpaca Imports ---
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.models import TradeAccount, Position, Order


# ==========================================
# 1. Custom Exceptions
# ==========================================
class TrustBridgeError(Exception):
    """Base exception for trust financial gateway errors."""
    pass

class PlaidServiceError(TrustBridgeError):
    """Raised when bank operations fail."""
    pass

class AlpacaServiceError(TrustBridgeError):
    """Raised when brokerage or trade execution fails."""
    pass


# ==========================================
# 2. Data Models (Strict Types)
# ==========================================
class BankAccountSnapshot(BaseModel):
    account_id: str
    name: str
    official_name: Optional[str] = None
    type: str
    subtype: str
    available_balance: Optional[Decimal] = None
    current_balance: Decimal
    currency: str = "USD"

class OrderRequestModel(BaseModel):
    symbol: str
    side: str  # "buy" or "sell"
    qty: Optional[float] = None
    notional: Optional[float] = Field(default=None, description="USD dollar value for fractional trading")
    order_type: str = "market"  # "market" or "limit"
    limit_price: Optional[float] = None
    time_in_force: str = "day"


# ==========================================
# 3. Plaid Bank Service Wrapper
# ==========================================
class PlaidBankService:
    def __init__(self, client_id: str, secret: str, env: str = "sandbox"):
        env_map = {
            "sandbox": plaid.Environment.Sandbox,
            "production": plaid.Environment.Production
        }
        if env not in env_map:
            raise ValueError(f"Invalid Plaid environment: {env}. Must be 'sandbox' or 'production'.")

        configuration = plaid.Configuration(
            host=env_map[env],
            api_key={
                "clientId": client_id,
                "secret": secret
            }
        )
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

    def fetch_balances(self, access_token: str) -> List[BankAccountSnapshot]:
        """Retrieves real-time cash & liquid account balances."""
        try:
            request = AccountsBalanceGetRequest(access_token=access_token)
            response = self.client.accounts_balance_get(request)
            
            snapshots = []
            for acc in response.accounts:
                curr = acc.balances.current
                avail = acc.balances.available
                
                snapshots.append(BankAccountSnapshot(
                    account_id=acc.account_id,
                    name=acc.name,
                    official_name=acc.official_name,
                    type=str(acc.type),
                    subtype=str(acc.subtype),
                    current_balance=Decimal(str(curr)) if curr is not None else Decimal("0.00"),
                    available_balance=Decimal(str(avail)) if avail is not None else None,
                    currency=acc.balances.iso_currency_code or "USD"
                ))
            return snapshots
        except Exception as e:
            raise PlaidServiceError(f"Failed to fetch Plaid account balances: {str(e)}") from e

    def sync_transactions(self, access_token: str, cursor: Optional[str] = None) -> Dict:
        """Fetches incremental transactions for accounting auto-categorization."""
        try:
            request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor or ""
            )
            response = self.client.transactions_sync(request)
            return response.to_dict()
        except Exception as e:
            raise PlaidServiceError(f"Failed to sync transactions: {str(e)}") from e

    def create_processor_token(self, access_token: str, account_id: str, processor: str = "alpaca") -> str:
        """Generates a secure processor token for direct bank-to-brokerage ACH funding."""
        try:
            request = ProcessorTokenCreateRequest(
                access_token=access_token,
                account_id=account_id,
                processor=processor
            )
            response = self.client.processor_token_create(request)
            return response.processor_token
        except Exception as e:
            raise PlaidServiceError(f"Failed to generate processor token: {str(e)}") from e


# ==========================================
# 4. Alpaca Brokerage Service Wrapper
# ==========================================
class AlpacaTreasuryService:
    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        self.client = TradingClient(api_key=api_key, secret_key=secret_key, paper=paper)

    def get_account_summary(self) -> Dict[str, Union[float, bool]]:
        """Extracts buying power, total portfolio equity, and operational cash."""
        try:
            account: TradeAccount = self.client.get_account()
            return {
                "equity": float(account.equity),
                "cash": float(account.cash),
                "buying_power": float(account.buying_power),
                "portfolio_value": float(account.portfolio_value),
                "pattern_day_trader": account.pattern_day_trader,
                "trading_blocked": account.trading_blocked
            }
        except Exception as e:
            raise AlpacaServiceError(f"Failed to fetch Alpaca account status: {str(e)}") from e

    def list_positions(self) -> List[Dict]:
        """Lists active trust portfolio assets."""
        try:
            positions: List[Position] = self.client.get_all_positions()
            return [
                {
                    "symbol": pos.symbol,
                    "qty": float(pos.qty),
                    "market_value": float(pos.market_value),
                    "cost_basis": float(pos.cost_basis),
                    "unrealized_pl": float(pos.unrealized_pl),
                    "current_price": float(pos.current_price)
                }
                for pos in positions
            ]
        except Exception as e:
            raise AlpacaServiceError(f"Failed to retrieve positions: {str(e)}") from e

    def execute_order(self, order_req: OrderRequestModel) -> Dict:
        """Submits structured buy/sell orders with fiduciary parameter validation."""
        try:
            side = OrderSide.BUY if order_req.side.lower() == "buy" else OrderSide.SELL
            tif = TimeInForce.DAY if order_req.time_in_force.lower() == "day" else TimeInForce.GTC

            if order_req.order_type.lower() == "market":
                order_data = MarketOrderRequest(
                    symbol=order_req.symbol,
                    qty=order_req.qty,
                    notional=order_req.notional,
                    side=side,
                    time_in_force=tif
                )
            elif order_req.order_type.lower() == "limit":
                if not order_req.limit_price:
                    raise ValueError("Limit orders require 'limit_price'.")
                order_data = LimitOrderRequest(
                    symbol=order_req.symbol,
                    qty=order_req.qty,
                    limit_price=order_req.limit_price,
                    side=side,
                    time_in_force=tif
                )
            else:
                raise ValueError(f"Unsupported order type: {order_req.order_type}")

            order: Order = self.client.submit_order(order_data=order_data)
            return {
                "order_id": str(order.id),
                "symbol": order.symbol,
                "status": str(order.status),
                "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
                "side": str(order.side),
                "qty": float(order.qty) if order.qty else None,
                "notional": float(order.notional) if order.notional else None
            }
        except Exception as e:
            raise AlpacaServiceError(f"Trade execution failed for {order_req.symbol}: {str(e)}") from e


# ==========================================
# 5. Integrated Gateway Orchestrator
# ==========================================
class TrustFinancialBridge:
    """Unified Orchestration Gateway for Trust Liquidity & Investment Execution."""

    def __init__(
        self,
        plaid_client_id: str,
        plaid_secret: str,
        alpaca_key: str,
        alpaca_secret: str,
        plaid_env: str = "sandbox",
        paper_trading: bool = True
    ):
        self.bank = PlaidBankService(client_id=plaid_client_id, secret=plaid_secret, env=plaid_env)
        self.treasury = AlpacaTreasuryService(api_key=alpaca_key, secret_key=alpaca_secret, paper=paper_trading)

    def assess_total_trust_liquidity(self, bank_access_token: str) -> Dict:
        """Aggregates banking cash reserves and brokerage portfolio value for real-time ledger auditing."""
        bank_accounts = self.bank.fetch_balances(access_token=bank_access_token)
        brokerage_summary = self.treasury.get_account_summary()

        total_bank_cash = sum(acc.available_balance or acc.current_balance for acc in bank_accounts)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "banking_cash_usd": float(total_bank_cash),
            "brokerage_cash_usd": brokerage_summary["cash"],
            "brokerage_equity_usd": brokerage_summary["equity"],
            "consolidated_liquid_trust_assets": float(total_bank_cash) + brokerage_summary["equity"],
            "bank_accounts": [acc.model_dump() for acc in bank_accounts]
        }
