"""
Module for posting updates to Notion databases and pages.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def update_task(notion, task_id, properties):
    """
    Update a task in Notion.
    
    Args:
        notion: Initialized Notion client
        task_id: ID of the task to update
        properties: Dictionary of properties to update
        
    Returns:
        Updated task object
    """
    try:
        logger.info(f"Updating task {task_id}")
        
        response = notion.pages.update(
            page_id=task_id,
            properties=properties
        )
        
        logger.info(f"Successfully updated task {task_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise

def create_task(notion, database_id, properties):
    """
    Create a new task in Notion.
    
    Args:
        notion: Initialized Notion client
        database_id: ID of the tasks database
        properties: Dictionary of properties for the new task
        
    Returns:
        Newly created task object
    """
    try:
        logger.info(f"Creating new task in database {database_id}")
        
        response = notion.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        
        logger.info(f"Successfully created task {response['id']}")
        return response
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise

def update_project_status(notion, project_id, status):
    """
    Update a project's status in Notion.
    
    Args:
        notion: Initialized Notion client
        project_id: ID of the project to update
        status: New status value
        
    Returns:
        Updated project object
    """
    try:
        logger.info(f"Updating project {project_id} status to {status}")
        
        response = notion.pages.update(
            page_id=project_id,
            properties={
                "Status": {
                    "status": {
                        "name": status
                    }
                }
            }
        )
        
        logger.info(f"Successfully updated project {project_id} status")
        return response
        
    except Exception as e:
        logger.error(f"Error updating project {project_id} status: {e}")
        raise

def append_to_page(notion, page_id, content_blocks):
    """
    Append content blocks to a Notion page.
    
    Args:
        notion: Initialized Notion client
        page_id: ID of the page to update
        content_blocks: List of block objects to append
        
    Returns:
        API response
    """
    try:
        logger.info(f"Appending content to page {page_id}")
        
        response = notion.blocks.children.append(
            block_id=page_id,
            children=content_blocks
        )
        
        logger.info(f"Successfully appended content to page {page_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error appending to page {page_id}: {e}")
        raise

def create_dashboard_update(notion, dashboard_id, title, content_blocks):
    """
    Create a new dashboard update entry.
    
    Args:
        notion: Initialized Notion client
        dashboard_id: ID of the dashboard database
        title: Title for the update
        content_blocks: List of block objects with the update content
        
    Returns:
        Newly created page object
    """
    try:
        logger.info(f"Creating dashboard update '{title}' in database {dashboard_id}")
        
        # Create the page with title
        page = notion.pages.create(
            parent={"database_id": dashboard_id},
            properties={
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                }
            }
        )
        
        # Append the content blocks
        if content_blocks:
            notion.blocks.children.append(
                block_id=page["id"],
                children=content_blocks
            )
        
        logger.info(f"Successfully created dashboard update {page['id']}")
        return page
        
    except Exception as e:
        logger.error(f"Error creating dashboard update: {e}")
        raise

def update_tariff_dashboard(notion, dashboard_page_id, tariff_data):
    """
    Update the TariffStrike dashboard in Notion.
    
    Args:
        notion: Initialized Notion client
        dashboard_page_id: ID of the dashboard page
        tariff_data: Dictionary containing tariff data to display
        
    Returns:
        Updated page object
    """
    try:
        logger.info(f"Updating TariffStrike dashboard {dashboard_page_id}")
        
        # Create content blocks based on tariff data
        content_blocks = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "TariffStrike Dashboard"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                            }
                        }
                    ]
                }
            },
            # Tariff data summary
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"Active arbitrage opportunities: {tariff_data.get('active_opportunities', 0)}"
                            },
                            "annotations": {
                                "bold": True
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"Total revenue generated: {tariff_data.get('total_revenue', '$0.00')}"
                            },
                            "annotations": {
                                "bold": True
                            }
                        }
                    ]
                }
            },
            # Divider
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            }
        ]
        
        # Add top opportunities if available
        if tariff_data.get('top_opportunities'):
            content_blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Top Opportunities"
                            }
                        }
                    ]
                }
            })
            
            for opp in tariff_data.get('top_opportunities', []):
                content_blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"{opp.get('name')} - Potential profit: {opp.get('profit')}"
                                }
                            }
                        ]
                    }
                })
        
        # Update the page with our content blocks
        # First, delete existing content (optional)
        # notion.blocks.children.list(block_id=dashboard_page_id)
        # ... code to delete existing blocks if necessary ...
        
        # Then append new content
        response = notion.blocks.children.append(
            block_id=dashboard_page_id,
            children=content_blocks
        )
        
        logger.info(f"Successfully updated TariffStrike dashboard {dashboard_page_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error updating TariffStrike dashboard: {e}")
        raise
