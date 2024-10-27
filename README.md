# Uniswap Liquidity Pool Monitor

A Python-based bot that monitors the ETH/ERG price on Uniswap and sends alerts via Telegram when the price gets close to specific thresholds. This bot is useful for liquidity providers who want to be notified when the price approaches their set price range, ensuring they can manage their liquidity effectively.

## Features
- Monitors the price of ETH/ERG based on data from CoinGecko.
- Sends alerts when the price is close to the set range.
- Configurable thresholds and alert margins.
- Responds to Telegram commands to display current price and thresholds.

## Getting Started

### Prerequisites
- Python 3.8 or above.
- A Telegram bot token and chat ID.

### Obtaining a Telegram Bot Token and Chat ID

1. **Create a Telegram Bot**:
   - Open Telegram and search for `BotFather`.
   - Start a chat with `BotFather` and create a new bot using the `/newbot` command.
   - Follow the prompts and you will receive a token for your bot, which looks like: `123456789:ABCDEF1234567890abcdef1234567890`.

2. **Get the Chat ID**:
   - Add your new bot to a Telegram chat (can be a private chat or group).
   - Send a message (e.g., `/start`) to your bot.
   - Use a web browser to navigate to the following URL (replace `YOUR_BOT_TOKEN` with your bot token):
     ```
     https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
     ```
   - Look for the `"chat"` object in the response. The `"id"` field in this object is your chat ID. It will look like this: `1234567890`.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/odiseusme/uniswap-liquidity-monitor.git
   ```

2. Navigate to the project directory:
   ```bash
   cd uniswap-liquidity-monitor
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file (optional but recommended) to securely store your Telegram credentials:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

5. Alternatively, you can directly set the environment variables in your terminal:
   ```bash
   export TELEGRAM_BOT_TOKEN=your_bot_token
   export TELEGRAM_CHAT_ID=your_chat_id
   ```

## Running the Bot

Run the bot using Python:
```bash
python liquidity_pool_monitor.py
```

The bot will start monitoring the ETH/ERG price based on the configured thresholds. It will also listen for the `"p"` command in Telegram to provide the current price and alert thresholds.

## Configuration

The bot’s behavior can be configured by modifying the `Config` class in `liquidity_pool_monitor.py`:

- **`UPPER_THRESHOLD`** and **`LOWER_THRESHOLD`**: Set the ETH/ERG thresholds for alerting.
- **`PRICE_MARGIN`**: Set the percentage margin for when alerts should trigger.
- **`PRICE_CHECK_INTERVAL`**: Time (in seconds) between each price check.
- **`ALERT_COOLDOWN`**: Cooldown time (in seconds) between consecutive alerts.

## Code Explanation

The code consists of the following main components:

1. **`PriceMonitor` Class**: Manages price monitoring, alerting, and Telegram messaging.
2. **`test_telegram_connection` Method**: Tests the Telegram bot connection on startup.
3. **`get_crypto_prices` Method**: Fetches ETH/ERG prices from the CoinGecko API.
4. **`send_telegram_message` Method**: Sends messages to the specified Telegram chat.
5. **`check_price` Method**: Checks the current price against the thresholds and sends alerts if necessary.
6. **`listen_for_messages` Method**: Listens for Telegram commands (like `"p"`) to provide real-time information.

## Contributing

Feel free to open issues and submit pull requests if you have any improvements or bug fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
