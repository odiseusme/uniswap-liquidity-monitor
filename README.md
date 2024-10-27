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

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/uniswap-liquidity-monitor.git
