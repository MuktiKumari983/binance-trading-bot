import time
import hmac
import hashlib
import logging
import requests

# This automatically creates a log file and prints updates to your screen at the same time
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trading_bot.log"),
        logging.StreamHandler()
    ]
)

# The official Testnet URL required by Primetrade.ai
BASE_URL = "https://testnet.binancefuture.com"

class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise ValueError("API Key and Secret Key must be provided.")
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {"X-MBX-APIKEY": self.api_key}

    def _generate_signature(self, query_string: str) -> str:
        """Encrypts the request parameters using your Secret Key (Required by Binance)"""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def get_order_status(self, symbol: str, order_id: int):
        """Fetches the latest execution status of a specific order (Required to get true MARKET order fills)"""
        endpoint = "/fapi/v1/order"
        timestamp = int(time.time() * 1000)
        
        params = {
            "symbol": symbol.upper(),
            "orderId": order_id,
            "timestamp": timestamp
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = self._generate_signature(query_string)
        full_url = f"{BASE_URL}{endpoint}?{query_string}&signature={signature}"
        
        try:
            response = requests.get(full_url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logging.error(f"Failed to fetch updated order status: {str(e)}")
        return None

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None):
        endpoint = "/fapi/v1/order"
        timestamp = int(time.time() * 1000) # Binance requires timestamps in milliseconds
        
        # Build the order details packet
        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity,
            "timestamp": timestamp
        }
        
        # Extra rule: Limit orders MUST have a target price and a Time-In-Force setting
        if order_type.upper() == "LIMIT":
            if not price:
                raise ValueError("Price is required for LIMIT orders.")
            params["price"] = price
            params["timeInForce"] = "GTC" # GTC means 'Good 'Til Cancelled'

        # Link all parameters together into a single web string and sign it
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = self._generate_signature(query_string)
        full_url = f"{BASE_URL}{endpoint}?{query_string}&signature={signature}"
        
        logging.info(f"Sending request to Binance -> {order_type} {side} {quantity} {symbol}")
        
        try:
            # Send the request over the internet
            response = requests.post(full_url, headers=self.headers)
            response_data = response.json()
            
            if response.status_code == 200:
                logging.info("Order successfully executed on Testnet!")
                
                # FIX: If it's a MARKET order, instantly query it again to catch the 'FILLED' status details
                if order_type.upper() == "MARKET" and "orderId" in response_data:
                    time.sleep(0.2) # Micro-pause to let the matching engine execute the fill
                    updated_data = self.get_order_status(symbol, response_data["orderId"])
                    if updated_data:
                        response_data = updated_data
                
                return True, response_data
            else:
                logging.error(f"Binance rejected the order: {response_data}")
                return False, response_data
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error (Check your internet connection): {str(e)}")
            return False, {"error": f"Network error: {str(e)}"}
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            return False, {"error": str(e)}