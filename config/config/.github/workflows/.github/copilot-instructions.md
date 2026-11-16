
import os
import yaml
import requests

def load_yaml(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def run_publisher():
    # Загружаем конфигурации из папки config
    config_dir = os.path.join(os.path.dirname(__file__), '../config')
    countries = load_yaml(os.path.join(config_dir, 'countries.yaml'))['countries']
    channels_config = load_yaml(os.path.join(config_dir, 'channels.yaml'))['channels']
    
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    print(f"Loaded {len(channels_config)} target channels for publishing.")
    
    for channel in channels_config:
        channel_id = channel['id']
        country_key = channel['country']
        tag = channel['associate_tag']
        
        country_limit = countries.get(country_key, {}).get('max_price_usd', 1000)
        print(f"Processing channel {channel_id} for country '{country_key}' (Limit: ${country_limit}, Tag: {tag})")
        
        # Здесь будет логика получения товаров (например, из Amazon PA-API)
        # И фильтрация по country_limit перед отправкой через Telegram Bot API

if __name__ == "__main__":
    run_publisher()
