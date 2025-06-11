import os
import json
import time
import requests
from datetime import datetime

DISCORD_WEBHOOK_URL = "Your Webhook URL"
SHOP_DATA_PATH = r"Your Xeno Workspace Location\shop_stock.json"
ITEM_ORDER = [
    "Carrot", "Strawberry", "Blueberry", "Orange Tulip", "Tomato",
    "Corn", "Daffodil", "Watermelon", "Pumpkin", "Apple",
    "Bamboo", "Coconut", "Cactus", "Dragon Fruit", "Mango",
    "Grape", "Mushroom", "Pepper", "Cacao", "Beanstalk", "Emberlilly"
]

def log(message, level="INFO"):
    """Enhanced logging with colors and consistent format"""
    colors = {
        "INFO": "\033[94m",    # Blue
        "SUCCESS": "\033[92m", # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
        "END": "\033[0m"       # Reset
    }
    print(f"{colors.get(level, '')}[{datetime.now().strftime('%H:%M:%S')}] {message}{colors['END']}")

def send_discord_message(message):
    """Improved Discord message sending with detailed status"""
    try:
        start_time = time.time()
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json={"content": message},
            timeout=10
        )
        response_time = (time.time() - start_time) * 1000
        response.raise_for_status()
        log(f"Discord response: {response.status_code} ({(response_time):.0f}ms)", "SUCCESS")
        return True
    except requests.exceptions.RequestException as e:
        log(f"Discord send failed: {str(e)}", "ERROR")
        return False

def process_stock_data():
    """Handles all file operations with detailed status reporting"""
    try:
        # Check if file exists and is readable
        if not os.path.exists(SHOP_DATA_PATH):
            log("Stock file not found", "WARNING")
            return None, None
        
        # Read and parse file
        with open(SHOP_DATA_PATH, 'r') as f:
            content = f.read()
            if not content.strip():
                log("Stock file is empty", "WARNING")
                return None, None
            
            data = json.loads(content)
            current_hash = hash(content)
            
            if "items" not in data:
                log("No 'items' key in stock data", "WARNING")
                return None, None
            
            return data["items"], current_hash
            
    except json.JSONDecodeError:
        log("Invalid JSON in stock file", "ERROR")
    except Exception as e:
        log(f"Unexpected file error: {str(e)}", "ERROR")
    return None, None

def generate_stock_message(stock_data):
    """Create formatted message with verification"""
    if not stock_data:
        return None
    
    message_lines = ["**🛒 Shop Stock Update**"]
    items_found = 0
    
    for item_name in ITEM_ORDER:
        if item_name in stock_data:
            message_lines.append(f"- {item_name}: {stock_data[item_name]}")
            items_found += 1
        else:
            message_lines.append(f"- {item_name}: Not available")
    
    log(f"Prepared message with {items_found} items in stock")
    return "\n".join(message_lines)

def monitor_loop():
    """Main monitoring loop with detailed state tracking"""
    last_hash = None
    consecutive_failures = 0
    max_failures = 5
    
    # Initialization
    log("🟢 LOADER STARTED", "SUCCESS")
    send_discord_message("**🟢 Loader Online!** Updating Shop Every Restock...")

    while consecutive_failures < max_failures:
        cycle_start = time.time()
        log("Starting monitoring cycle...")
        
        try:
            # Process stock data
            stock_data, current_hash = process_stock_data()
            
            if stock_data is not None:
                # Only send if data changed
                if current_hash != last_hash:
                    message = generate_stock_message(stock_data)
                    if message:
                        if send_discord_message(message):
                            log("Stock update successfully sent to Discord", "SUCCESS")
                            last_hash = current_hash
                            consecutive_failures = 0  # Reset failure counter
                        else:
                            consecutive_failures += 1
                    else:
                        log("No valid message generated", "WARNING")
                else:
                    log("No changes detected in stock data", "INFO")
            else:
                consecutive_failures += 1
            
            # Calculate precise sleep time
            cycle_time = time.time() - cycle_start
            sleep_time = max(60 - cycle_time, 1)  # Never sleep less than 1s
            log(f"Cycle completed in {cycle_time:.2f}s, sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            log("🟠 Loader stopped by user", "WARNING")
            send_discord_message("**🟠 Loader Stopped Manually**")
            break
        except Exception as e:
            consecutive_failures += 1
            log(f"CRITICAL ERROR: {str(e)}", "ERROR")
            time.sleep(30)  # Wait before retrying after error
    
    if consecutive_failures >= max_failures:
        log("🔴 Loader stopped due to too many failures", "ERROR")
        send_discord_message("**🔴 Loader Crashed** After multiple failures")

if __name__ == "__main__":
    monitor_loop()
