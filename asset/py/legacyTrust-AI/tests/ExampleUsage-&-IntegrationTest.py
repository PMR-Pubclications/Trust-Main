if __name__ == "__main__":
    # Load environment variables
    PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID", "your_plaid_client_id")
    PLAID_SECRET = os.getenv("PLAID_SECRET", "your_plaid_secret")
    PLAID_ACCESS_TOKEN = os.getenv("PLAID_ACCESS_TOKEN", "access-sandbox-xxx")
    
    ALPACA_KEY = os.getenv("ALPACA_API_KEY", "your_alpaca_key")
    ALPACA_SECRET = os.getenv("ALPACA_SECRET_KEY", "your_alpaca_secret")

    # Initialize the Unified Trust Bridge
    bridge = TrustFinancialBridge(
        plaid_client_id=PLAID_CLIENT_ID,
        plaid_secret=PLAID_SECRET,
        alpaca_key=ALPACA_KEY,
        alpaca_secret=ALPACA_SECRET,
        plaid_env="sandbox",
        paper_trading=True
    )

    # 1. Audit Liquidity
    liquidity_snapshot = bridge.assess_total_trust_liquidity(bank_access_token=PLAID_ACCESS_TOKEN)
    print("--- CONSOLIDATED TRUST LIQUIDITY ---")
    print(f"Total Liquid Net Worth: ${liquidity_snapshot['consolidated_liquid_trust_assets']:,.2f}")
    print(f"Bank Cash: ${liquidity_snapshot['banking_cash_usd']:,.2f}")
    print(f"Brokerage Cash: ${liquidity_snapshot['brokerage_cash_usd']:,.2f}")

    # 2. Execute a Dollar-Cost Averaging (DCA) Trade ($500 into SPY)
    dca_trade = OrderRequestModel(
        symbol="SPY",
        side="buy",
        notional=500.00,  # Fractional dollar-based buying
        order_type="market"
    )
    order_result = bridge.treasury.execute_order(dca_trade)
    print("\n--- DCA TREASURY ORDER EXECUTED ---")
    print(order_result)
