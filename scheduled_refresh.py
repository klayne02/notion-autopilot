"""
Scheduled refresh for Notion databases.
This script can be run at regular intervals to update Notion data.
"""
import atexit

def flush_logs():
    logging.shutdown()

atexit.register(flush_logs)


import time
import schedule
import logging
import os
from datetime import datetime
from basic_operations import load_config, initialize_notion_client, list_database_items

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/refresh.log"),
        logging.StreamHandler()  # This will output to console as well
    ]
)
logger = logging.getLogger(__name__)

def perform_refresh():
    """Perform a refresh of Notion databases."""
    logger.info(f"Starting scheduled refresh at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Load configuration
        config = load_config()
        notion = initialize_notion_client(config)
        
        # Refresh projects database
        projects_db = config.get('projects_db')
        if projects_db:
            logger.info("Refreshing projects database")
            projects = list_database_items(notion, projects_db)
            logger.info(f"Found {len(projects)} projects")
        
        logger.info("Refresh completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error during refresh: {e}")
        return False

def start_scheduler(interval_minutes=60):
    """Start the scheduler to run refreshes at regular intervals."""
    logger.info(f"Starting scheduler with {interval_minutes} minute interval")
    
    # Schedule the refresh job
    schedule.every(interval_minutes).minutes.do(perform_refresh)
    
    # Run once immediately
    logger.info("Running initial refresh...")
    perform_refresh()
    
    # Keep the scheduler running
    logger.info(f"Scheduler running. Press Ctrl+C to exit.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")

if __name__ == "__main__":
    # Run with a 60-minute interval
    start_scheduler(60)