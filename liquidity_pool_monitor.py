import requests
import time
import threading
from datetime import datetime
import os
from typing import Dict, Optional, Tuple

# Environment variables for sensitive data (better security)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '123456789:ABCDEF1234567890abcdef1234567890')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '222222222')

# Configuration
class Config:
    UPPER_THRESHOLD: float = 5135.2
    LOWER_THRESHOLD: float = 2992.61
    PRICE_CHECK_INTERVAL: int = 300  # 5 minutes
    MESSAGE_CHECK_INTERVAL: int = 1   # 1 second
    RETRY_DELAY: int = 30            # 30 seconds
    MAX_RETRIES: int = 3
    ALERT_COOLDOWN: int = 3600  # 1 hour cooldown between alerts
    PRICE_MARGIN: float = 0.10   # 10% margin for threshold alerts

# API URLs
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

class PriceMonitor:
    def __init__(self):
        self.last_alert_time: Dict[str, float] = {}
        self.last_prices: Dict[str, float] = {}
        self.test_telegram_connection()

    def test_telegram_connection(self):
        """Test the Telegram bot connection on startup."""
        try:
            response = requests.get(f"{TELEGRAM_API_URL}/getMe")
            if response.status_code != 200:
                print(f"Error: Could not connect to Telegram bot. Status code: {response.status_code}")
                print(f"Response: {response.text}")
            else:
                print("Successfully connected to Telegram bot!")
        except Exception as e:
            print(f"Error connecting to Telegram bot: {e}")

    def get_crypto_prices(self) -> Optional[Tuple[float, float, float]]:
        """Fetch ERG and ETH prices from CoinGecko API."""
        params = {
            'ids': 'ergo,ethereum',
            'vs_currencies': 'usd,eth'
        }
        
        for attempt in range(Config.MAX_RETRIES):
            try:
                response = requests.get(COINGECKO_API_URL, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                erg_usd = data['ergo']['usd']
                eth_usd = data['ethereum']['usd']
                erg_eth = data['ergo']['eth']
                
                self.last_prices = {
                    'erg_usd': erg_usd,
                    'eth_usd': eth_usd,
                    'erg_eth': erg_eth
                }
                
                return erg_usd, eth_usd, erg_eth
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < Config.MAX_RETRIES - 1:
                    time.sleep(Config.RETRY_DELAY)
                else:
                    print("Max retries reached, using last known prices if available")
                    if self.last_prices:
                        return (
                            self.last_prices['erg_usd'],
                            self.last_prices['eth_usd'],
                            self.last_prices['erg_eth']
                        )
        return None

    def send_telegram_message(self, message: str) -> bool:
        """Send a message to Telegram with retry logic."""
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        for attempt in range(Config.MAX_RETRIES):
            try:
                response = requests.post(url, data=payload, timeout=10)
                response.raise_for_status()
                print(f"Message sent successfully: {message[:50]}...")  # Debug log
                return True
            except Exception as e:
                print(f"Telegram send attempt {attempt + 1} failed: {e}")
                if attempt < Config.MAX_RETRIES - 1:
                    time.sleep(Config.RETRY_DELAY)
        return False

    def format_price_message(self, eth_per_erg: float) -> str:
        """Format price information message."""
        upper_margin = Config.UPPER_THRESHOLD * (1 - Config.PRICE_MARGIN)
        lower_margin = Config.LOWER_THRESHOLD * (1 + Config.PRICE_MARGIN)
        
        return (
            f"💰 <b>ETH per ERG Price</b> ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n\n"
            f"ETH/ERG: {eth_per_erg:,.2f}\n"
            f"Target Range: {Config.LOWER_THRESHOLD:,.2f} - {Config.UPPER_THRESHOLD:,.2f}\n"
            f"You will get an alert when the ETH/ERG price is above {upper_margin:,.2f} or below {lower_margin:,.2f}."
        )

    def check_price(self) -> None:
        """Check prices and send alerts if thresholds are crossed."""
        prices = self.get_crypto_prices()
        if not prices:
            return

        erg_usd, eth_usd, erg_eth = prices
        eth_per_erg = 1 / erg_eth if erg_eth != 0 else 0  # Calculate ETH per ERG

        current_time = time.time()

        # Calculate the margins as 10% of the thresholds
        lower_margin = Config.LOWER_THRESHOLD * (1 + Config.PRICE_MARGIN)
        upper_margin = Config.UPPER_THRESHOLD * (1 - Config.PRICE_MARGIN)

        if current_time - self.last_alert_time.get('threshold', 0) > Config.ALERT_COOLDOWN:
            if eth_per_erg >= upper_margin:
                self.send_telegram_message(f"🚀 ETH/ERG is close to the upper edge ({Config.UPPER_THRESHOLD:,.2f})\n" + 
                                           self.format_price_message(eth_per_erg))
                self.last_alert_time['threshold'] = current_time
            elif eth_per_erg <= lower_margin:
                self.send_telegram_message(f"⚠️ ETH/ERG is close to the lower edge ({Config.LOWER_THRESHOLD:,.2f})\n" + 
                                           self.format_price_message(eth_per_erg))
                self.last_alert_time['threshold'] = current_time

    def get_updates(self, offset: Optional[int] = None) -> list:
        """Fetch new messages from Telegram."""
        url = f"{TELEGRAM_API_URL}/getUpdates"
        params = {'offset': offset, 'timeout': 30}
        try:
            response = requests.get(url, params=params, timeout=35)
            response.raise_for_status()
            updates = response.json().get('result', [])
            if updates:
                print(f"Received {len(updates)} new updates")  # Debug log
            return updates
        except Exception as e:
            print(f"Error fetching updates: {e}")
            return []

    def handle_updates(self, updates: list) -> None:
        """Process incoming Telegram updates."""
        for update in updates:
            try:
                message = update.get('message', {})
                text = message.get('text', '').lower()
                chat_id = str(message.get('chat', {}).get('id', ''))
                
                print(f"Received message: '{text}' from chat_id: {chat_id}")  # Debug log
                
                if chat_id == TELEGRAM_CHAT_ID and text == 'p':
                    print("Processing price command...")  # Debug log
                    prices = self.get_crypto_prices()
                    if prices:
                        erg_usd, eth_usd, erg_eth = prices
                        eth_per_erg = 1 / erg_eth if erg_eth != 0 else 0  # Calculate ETH per ERG
                        self.send_telegram_message(self.format_price_message(eth_per_erg))
                    else:
                        self.send_telegram_message("⚠️ Could not fetch prices. Please try again later.")
            except Exception as e:
                print(f"Error handling update: {e}")

    def listen_for_messages(self) -> None:
        """Message listening loop."""
        last_update_id = None
        print("Starting message listener...")  # Debug log
        
        while True:
            try:
                updates = self.get_updates(last_update_id)
                if updates:
                    last_update_id = updates[-1]['update_id'] + 1
                    self.handle_updates(updates)
                time.sleep(Config.MESSAGE_CHECK_INTERVAL)
            except Exception as e:
                print(f"Error in message listening: {e}")
                time.sleep(Config.RETRY_DELAY)

    def monitor_prices(self) -> None:
        """Price monitoring loop."""
        while True:
            try:
                self.check_price()
                time.sleep(Config.PRICE_CHECK_INTERVAL)
            except Exception as e:
                print(f"Error in price monitoring: {e}")
                time.sleep(Config.RETRY_DELAY)

def main():
    monitor = PriceMonitor()
    
    # Start price monitoring thread
    price_thread = threading.Thread(target=monitor.monitor_prices, daemon=True)
    price_thread.start()
    
    # Start message listening (main thread)
    monitor.listen_for_messages()

if __name__ == "__main__":
    main()
