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
        print("✅ STATUS: SUCCESS")
        print(f"📝 Order ID:      {result.get('orderId')}")
        print(f"📈 Order Status:   {result.get('status')}")
        print(f"📦 Executed Qty:  {result.get('executedQty')}")
        print(f"💵 Avg Price:     {result.get('avgPrice', 'N/A')}")
    else:
        print("❌ STATUS: FAILED")
        print(f"⚠️ Message: {result.get('msg', result)}")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()