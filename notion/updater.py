"""
Main updater module for Notion AutoPilot.
This module coordinates reading and writing data to Notion.
"""

import logging
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from notion_client import Client
import os 
# Import other modules
from . import fetch_pages
from . import post_tasks

# Set up logging
# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/notion_autopilot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from environment variables."""
    load_dotenv('config/.env')
    
    config = {
        'notion_api_key': os.getenv('NOTION_API_KEY'),
        'notion_version': os.getenv('NOTION_VERSION', '2022-06-28'),
        'projects_db': os.getenv('NOTION_PROJECTS_DB'),
        'tasks_db': os.getenv('NOTION_TASKS_DB'),
        'prompts_db': os.getenv('NOTION_PROMPTS_DB'),
        'dashboards_db': os.getenv('NOTION_DASHBOARDS_DB'),
        'enable_tariffstrike': os.getenv('ENABLE_TARIFFSTRIKE_SYNC', 'false').lower() == 'true',
        'update_interval': int(os.getenv('UPDATE_INTERVAL', 60)),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'enable_changelog': os.getenv('ENABLE_CHANGELOG', 'true').lower() == 'true'
    }
    
    # Set log level from config
    logger.setLevel(getattr(logging, config['log_level']))
    
    return config

def initialize_notion_client(config):
    """Initialize and return a Notion client."""
    try:
        # Simple initialization for notion-client 2.x
        notion = Client(auth=config['notion_api_key'])
        logger.info("Notion client initialized successfully")
        return notion
    except Exception as e:
        logger.error(f"Failed to initialize Notion client: {e}")
        raise

def update_changelog(message, status="INFO"):
    """Update the changelog CSV with a new entry."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Create changelog file if it doesn't exist
        if not os.path.exists('data/changelog.csv'):
            with open('data/changelog.csv', 'w') as f:
                f.write("timestamp,status,message\n")
        
        # Append the new entry
        with open('data/changelog.csv', 'a') as f:
            f.write(f"{timestamp},{status},{message}\n")
            
        logger.debug(f"Added to changelog: {message}")
    except Exception as e:
        logger.error(f"Failed to update changelog: {e}")

def run_update():
    """Main function to run the Notion update process."""
    logger.info("Starting Notion AutoPilot update process")
    
    # Load configuration
    config = load_config()
    
    # Initialize Notion client
    notion = initialize_notion_client(config)
    
    try:
        # Fetch data from Notion
        logger.info("Fetching data from Notion databases")
        projects = fetch_pages.get_projects(notion, config['projects_db'])
        tasks = fetch_pages.get_tasks(notion, config['tasks_db'])
        
        # Process data (this would be where you implement your business logic)
        logger.info("Processing data")
        # Example: Mark overdue tasks
        # processed_tasks = process_tasks(tasks)
        
        # Update Notion with processed data
        logger.info("Posting updates back to Notion")
        # Example: Update task status
        # post_tasks.update_tasks(notion, processed_tasks)
        
        # If enabled, fetch TariffStrike data and update related Notion pages
        if config['enable_tariffstrike']:
            logger.info("Syncing TariffStrike data")
            # Implement TariffStrike integration
            # tariff_data = fetch_tariff_data()
            # post_tasks.update_tariff_dashboard(notion, tariff_data)
        
        # Update local cache
        # cache_data = {
        #     'last_update': datetime.now().isoformat(),
        #     'projects_count': len(projects),
        #     'tasks_count': len(tasks)
        # }
        # with open('data/updates.json', 'w') as f:
        #     json.dump(cache_data, f)
        
        # Update changelog if enabled
        if config['enable_changelog']:
            update_changelog("Successful Notion update")
            
        logger.info("Notion update process completed successfully")
        
    except Exception as e:
        logger.error(f"Error during Notion update process: {e}")
        if config['enable_changelog']:
            update_changelog(f"Error: {str(e)}", "ERROR")
        raise

if __name__ == "__main__":
    run_update()
