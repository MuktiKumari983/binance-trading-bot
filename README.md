# Simplified Binance Futures Testnet Trading Bot

This clean, lightweight Python command-line utility connects directly to the Binance Futures Testnet (USDT-M) to execute market and limit orders securely.

## Project Structure
- `client.py`: Core API client that manages transaction signing, web requests, and robust error management.
- `cli.py`: User-facing terminal engine built using Python's native `argparse`.
- `requirements.txt`: Project dependency listing.

## How to Set Up & Run

1. Open your terminal and install the required web package:
```bash
   pip install -r requirements.txt