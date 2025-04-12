"""
Basic operations for interacting with Notion databases.
This script demonstrates reading, creating, and updating entries.
"""

import os
from dotenv import load_dotenv
from notion_client import Client
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from environment variables."""
    load_dotenv('config/.env')
    return {
        'notion_api_key': os.getenv('NOTION_API_KEY'),
        'projects_db': os.getenv('NOTION_PROJECTS_DB'),
        'tasks_db': os.getenv('NOTION_TASKS_DB')
    }

def initialize_notion_client(config):
    """Initialize the Notion client."""
    return Client(auth=config['notion_api_key'])

def list_database_items(notion, database_id):
    """List all items in a Notion database."""
    logger.info(f"Fetching items from database {database_id}")
    
    response = notion.databases.query(database_id=database_id)
    items = response.get('results', [])
    
    logger.info(f"Found {len(items)} items")
    for item in items:
        # Extract the title property (usually called "Name")
        title = "Untitled"
        for prop_name, prop_data in item['properties'].items():
            if prop_data.get('type') == 'title' and prop_data.get('title'):
                title = prop_data['title'][0]['text']['content'] if prop_data['title'] else "Untitled"
                break
        
        logger.info(f"- {title} (ID: {item['id']})")
    
    return items

def create_new_entry(notion, database_id, title, status=None):
    """Create a new entry in a Notion database."""
    logger.info(f"Creating new entry: {title}")
    
    # First, get database metadata to understand its structure
    database = notion.databases.retrieve(database_id=database_id)
    
    # Find the title property and status property
    title_property = None
    status_property = None
    status_options = []
    
    for prop_name, prop_data in database['properties'].items():
        if prop_data['type'] == 'title':
            title_property = prop_name
        elif prop_data['type'] == 'status':
            status_property = prop_name
            if 'status' in prop_data and 'options' in prop_data['status']:
                status_options = [option['name'] for option in prop_data['status']['options']]
    
    logger.info(f"Found title property: {title_property}")
    logger.info(f"Found status property: {status_property}")
    logger.info(f"Available status options: {status_options}")
    
    # Prepare properties based on actual database structure
    properties = {}
    
    # Add title property if found
    if title_property:
        properties[title_property] = {
            "title": [{"text": {"content": title}}]
        }
    else:
        logger.error("Could not find title property in database")
        return None
    
    # Add status if found and status parameter is provided
    if status_property and status:
        # Check if provided status is valid, otherwise use first available option
        if status in status_options:
            properties[status_property] = {"status": {"name": status}}
        elif status_options:
            logger.warning(f"Status '{status}' not found. Using '{status_options[0]}' instead.")
            properties[status_property] = {"status": {"name": status_options[0]}}
    elif status_property and status_options:
        # Use first available status option if none specified
        logger.info(f"No status specified. Using '{status_options[0]}' by default.")
        properties[status_property] = {"status": {"name": status_options[0]}}
    
    try:
        new_page = notion.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        
        logger.info(f"Created new entry with ID: {new_page['id']}")
        return new_page['id']
    except Exception as e:
        logger.error(f"Error creating entry: {e}")
        return None

def update_entry_status(notion, page_id, new_status):
    """Update the status of an existing entry."""
    if not page_id:
        logger.error("Cannot update entry: No page ID provided")
        return False
        
    logger.info(f"Updating entry {page_id} to status: {new_status}")
    
    try:
        # First get the page to find the status property name
        page = notion.pages.retrieve(page_id=page_id)
        
        # Find the status property
        status_property = None
        for prop_name, prop_data in page['properties'].items():
            if prop_data['type'] == 'status':
                status_property = prop_name
                break
        
        if not status_property:
            logger.error("Could not find status property in the page")
            return False
        
        # Update the page
        notion.pages.update(
            page_id=page_id,
            properties={
                status_property: {
                    "status": {
                        "name": new_status
                    }
                }
            }
        )
        
        logger.info(f"Updated entry status successfully")
        return True
    except Exception as e:
        logger.error(f"Error updating entry status: {e}")
        return False

def run_demo():
    """Run a demonstration of basic Notion operations."""
    # Load configuration and initialize client
    config = load_config()
    notion = initialize_notion_client(config)
    
    # Use the projects database for the demo
    database_id = config['projects_db']
    
    if not database_id:
        logger.error("No database ID found in configuration")
        return
    
    logger.info("STEP 1: Listing current database entries")
    items = list_database_items(notion, database_id)
    
    logger.info("\nSTEP 2: Creating a new entry")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_id = create_new_entry(
        notion, 
        database_id, 
        f"Test Entry from Notion AutoPilot - {timestamp}"
        # Let the function determine valid status options
    )
    
    logger.info("\nSTEP 3: Listing entries to see our new entry")
    updated_items = list_database_items(notion, database_id)
    
    # Only try updating if we successfully created an entry
    if new_id:
        logger.info("\nSTEP 4: Updating the status of our new entry")
        
        # Get available status options for this database
        database = notion.databases.retrieve(database_id=database_id)
        status_options = []
        for prop_name, prop_data in database['properties'].items():
            if prop_data['type'] == 'status' and 'status' in prop_data and 'options' in prop_data['status']:
                status_options = [option['name'] for option in prop_data['status']['options']]
                break
        
        # Choose a different status than the current one
        if status_options and len(status_options) > 1:
            new_status = status_options[1]  # Use the second option
            update_entry_status(notion, new_id, new_status)
        
        logger.info("\nSTEP 5: Listing entries again to verify the update")
        list_database_items(notion, database_id)
    else:
        logger.warning("Skipping status update as no entry was created")
    
    logger.info("\nDemo completed successfully!")

if __name__ == "__main__":
    run_demo()