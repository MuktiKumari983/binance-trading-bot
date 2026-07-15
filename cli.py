import argparse
import os
from client import BinanceFuturesClient

def main():
    # Setup our command-line input rules
    parser = argparse.ArgumentParser(description="Primetrade.ai Trading Bot CLI")
    parser.add_argument("--symbol", type=str, required=True, help="e.g., BTCUSDT")
    parser.add_argument("--side", type=str, required=True, choices=["BUY", "SELL"])
    parser.add_argument("--type", type=str, required=True, choices=["MARKET", "LIMIT"])
    parser.add_argument("--quantity", type=float, required=True)
    parser.add_argument("--price", type=float, help="Only needed for LIMIT orders")

    args = parser.parse_args()

    # Smart Validation check before even calling Binance
    if args.type.upper() == "LIMIT" and not args.price:
        print("\n❌ Error: You must provide a --price when placing a LIMIT order!")
        return

    # Securely read your keys from your laptop's environment settings
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        print("\n❌ Error: Keys missing! Please set BINANCE_API_KEY and BINANCE_API_SECRET variables.")
        return

    # Requirement 4: Print a clean request summary
    print("\n" + "="*40)
    print("         ORDER REQUEST SUMMARY")
    print("="*40)
    print(f"🔹 Trading Pair: {args.symbol.upper()}")
    print(f"🔹 Action:       {args.side.upper()}")
    print(f"🔹 Execution:    {args.type.upper()}")
    print(f"🔹 Quantity:     {args.quantity}")
    if args.price:
        print(f"🔹 Target Price: {args.price}")
    print("="*40 + "\n")

    # Start the engine
    bot = BinanceFuturesClient(api_key, api_secret)
    
    # Run the trade
    success, result = bot.place_order(
        symbol=args.symbol,
        side=args.side,
        order_type=args.type,
        quantity=args.quantity,
        price=args.price
    )

    # Requirement 4: Print a clean response summary
    print("\n" + "="*40)
    print("         BINANCE RESPONSE DETAILS")
    print("="*40)
    if success:
        # Extract the fields safely using fallback keys
        status = result.get("status", "UNKNOWN")
        
        # Check 'cumQty' if 'executedQty' is empty or zero
        executed_qty = result.get("executedQty")
        if not executed_qty or float(executed_qty) == 0:
            executed_qty = result.get("cumQty", "0.0000")
            
        # Extract or dynamically calculate average price
        avg_price = result.get("avgPrice")
        if not avg_price or float(avg_price) == 0:
            cum_quote = float(result.get("cumQuote", 0))
            exec_qty_val = float(executed_qty)
            if exec_qty_val > 0 and cum_quote > 0:
                avg_price = f"{cum_quote / exec_qty_val:.2f}"
            else:
                avg_price = result.get("price", "N/A")

        print("✅ STATUS: SUCCESS")
        print(f"📝 Order ID:      {result.get('orderId')}")
        print(f"📈 Order Status:   {status}")
        print(f"📦 Executed Qty:   {executed_qty}")
        print(f"💵 Avg Price:      {avg_price}")
    else:
        print("❌ STATUS: FAILED")
        print(f"⚠️ Message: {result.get('msg', result)}")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()