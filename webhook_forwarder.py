import os
import json
import time
import requests
from datetime import datetime

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1382116486923026553/eoIaWbEvZkNejedPw5fv_o8TVZX7yf6vF2XjeGiz8QGiH_2V5-pViSmeZheumf8EjycL"
SHOP_DATA_PATH = r"C:\Users\sh5\Downloads\Xeno-v1.2.25-e6d3d66b\Xeno-v1.2.25\workspace\shop_stock.json"
GEAR_DATA_PATH = r"C:\Users\sh5\Downloads\Xeno-v1.2.25-e6d3d66b\Xeno-v1.2.25\workspace\gear_stock.json"

ITEM_EMOJIS = {
    "Carrot": "🥕",
    "Strawberry": "🍓",
    "Blueberry": "🫐",
    "Orange Tulip": "🌷",
    "Tomato": "🍅",
    "Corn": "🌽",
    "Daffodil": "🌼",
    "Watermelon": "🍉",
    "Pumpkin": "🎃",
    "Apple": "🍎",
    "Bamboo": "🎍",
    "Coconut": "🥥",
    "Cactus": "🌵",
    "Dragon Fruit": "🐉",
    "Mango": "🥭",
    "Grape": "🍇",
    "Mushroom": "🍄",
    "Pepper": "🌶️",
    "Cacao": "🍫",
    "Beanstalk": "🌱",
    "Ember Lily": "🔥"
}

# You can add gear-specific items here or leave empty to just show keys as-is
GEAR_ITEM_EMOJIS = {
    # Example gear emojis, adjust or extend if you want
    "Advanced Sprinkler": "💧",
    "Master Sprinkler": "🚿",
    "Trowel": "🔧",
    "Friendship Pot": "🌿",
    "Harvest Tool": "🛠️",
    "Watering Can": "🚿",
    "Recall Wrench": "🔩",
    "Favorite Tool": "⭐",
    "Basic Sprinkler": "💧",
    "Lightning Rod": "⚡",
    "Godly Sprinkler": "🌟"
}

def log(message, level="INFO"):
    colors = {
        "INFO": "\033[94m",    # Blue
        "SUCCESS": "\033[92m", # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
        "END": "\033[0m"       # Reset
    }
    print(f"{colors.get(level, '')}[{datetime.now().strftime('%H:%M:%S')}] {message}{colors['END']}")

def send_discord_message(message, embed=False, status=None, title=None, thumbnail_url=None):
    try:
        # Default thumbnails based on status if no thumbnail_url explicitly provided
        default_thumbnails = {
            "online": "https://emojicdn.elk.sh/🟢?size=96",
            "warning": "https://emojicdn.elk.sh/🟠?size=96",
            "error": "https://emojicdn.elk.sh/🔴?size=96",
            "default": "https://emojicdn.elk.sh/🍃?size=96"
        }
        
        thumb_url = thumbnail_url or default_thumbnails.get(status, default_thumbnails["default"])
        
        payload = {
            "content": None if embed else message,
            "embeds": [
                {
                    "title": title if title else ("🛒 Shop Stock Update" if status is None else message.split('\n')[0]),
                    "description": message if embed else None,
                    "color": {
                        "online": 0x77b255,
                        "warning": 0xffcc4d,
                        "error": 0xdd2e44,
                        None: 0x77b255
                    }.get(status),
                    "thumbnail": {"url": thumb_url},
                    "footer": {
                        "text": f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                }
            ] if embed else None
        }
        start_time = time.time()
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        response_time = (time.time() - start_time) * 1000
        log(f"Discord response: {response.status_code} ({response_time:.0f}ms)", "SUCCESS")
        return True
    except requests.exceptions.RequestException as e:
        log(f"Discord send failed: {str(e)}", "ERROR")
        return False

def read_stock_file(path):
    if not os.path.exists(path):
        log(f"File not found: {path}", "WARNING")
        return None, None
    try:
        with open(path, 'r') as f:
            content = f.read()
            if not content.strip():
                log(f"File empty: {path}", "WARNING")
                return None, None
            data = json.loads(content)
            return data.get("items", {}), hash(content)
    except json.JSONDecodeError:
        log(f"Invalid JSON in file: {path}", "ERROR")
        return None, None

def generate_message_for_shop(shop_name, stock_data, emojis_map):
    if not stock_data:
        return f"**{shop_name}**\n_No stock data available._"
    message_lines = [f"__**{shop_name}**__"]
    for item_name, stock_value in stock_data.items():
        emoji = emojis_map.get(item_name, "❓")
        message_lines.append(f"{emoji} **{item_name}:** `{stock_value}`")
    return "\n".join(message_lines)

def monitor_loop():
    last_seed_hash = None
    last_gear_hash = None
    consecutive_failures = 0
    max_failures = 5

    log("🟢 LOADER STARTED", "SUCCESS")
    send_discord_message(
        "**🟢 Loader Online!** Monitoring shop restocks...",
        embed=True,
        status="online",
        title="Loader Status",
        thumbnail_url="https://emojicdn.elk.sh/🟢?size=96"
    )

    while consecutive_failures < max_failures:
        cycle_start = time.time()
        log("Starting monitoring cycle...")

        try:
            seed_stock, seed_hash = read_stock_file(SHOP_DATA_PATH)
            gear_stock, gear_hash = read_stock_file(GEAR_DATA_PATH)

            if seed_stock is None and gear_stock is None:
                log("No valid stock data available for either shop.", "WARNING")
                consecutive_failures += 1
            else:
                # Send Seed Shop update if changed
                if seed_hash != last_seed_hash and seed_stock is not None:
                    message = generate_message_for_shop("Seed Shop", seed_stock, ITEM_EMOJIS)
                    if send_discord_message(
                        message,
                        embed=True,
                        status="online",
                        title="Seed Shop Stock Update",
                        thumbnail_url="https://emojicdn.elk.sh/🍃?size=96"
                    ):
                        log("Seed Shop stock update sent.", "SUCCESS")
                        last_seed_hash = seed_hash
                        consecutive_failures = 0
                    else:
                        log("Failed to send Seed Shop stock update.", "ERROR")
                        consecutive_failures += 1
                else:
                    log("No changes detected in Seed Shop stock.", "INFO")

                # Send Gear Shop update if changed
                if gear_hash != last_gear_hash and gear_stock is not None:
                    message = generate_message_for_shop("Gear Shop", gear_stock, GEAR_ITEM_EMOJIS)
                    if send_discord_message(
                        message,
                        embed=True,
                        status="online",
                        title="Gear Shop Stock Update",
                        thumbnail_url="https://emojicdn.elk.sh/⚙️?size=96"
                    ):
                        log("Gear Shop stock update sent.", "SUCCESS")
                        last_gear_hash = gear_hash
                        consecutive_failures = 0
                    else:
                        log("Failed to send Gear Shop stock update.", "ERROR")
                        consecutive_failures += 1
                else:
                    log("No changes detected in Gear Shop stock.", "INFO")

            cycle_time = time.time() - cycle_start
            sleep_time = max(60 - cycle_time, 1)
            log(f"Cycle completed in {cycle_time:.2f}s, sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            log("🟠 Loader stopped by user", "WARNING")
            send_discord_message(
                "**🟠 Loader Stopped Manually**",
                embed=True,
                status="warning",
                title="Loader Stopped"
            )
            break
        except Exception as e:
            log(f"CRITICAL ERROR: {str(e)}", "ERROR")
            consecutive_failures += 1
            time.sleep(30)

    if consecutive_failures >= max_failures:
        log("🔴 Loader stopped due to too many failures", "ERROR")
        send_discord_message(
            "**🔴 Loader Crashed** After multiple failures", embed=True, status="error")

if __name__ == "__main__":
    monitor_loop()
