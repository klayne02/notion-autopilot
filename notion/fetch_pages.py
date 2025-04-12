"""
Module for fetching data from Notion databases.
"""

import logging
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

def get_projects(notion, database_id):
    """
    Fetch projects from Notion database.
    
    Args:
        notion: Initialized Notion client
        database_id: ID of the projects database
        
    Returns:
        List of project objects
    """
    try:
        logger.info(f"Fetching projects from database {database_id}")
        
        response = notion.databases.query(
            database_id=database_id,
            filter={
                "property": "Status",
                "status": {
                    "does_not_equal": "Completed"
                }
            },
            sorts=[
                {
                    "property": "Priority",
                    "direction": "descending"
                }
            ]
        )
        
        projects = response.get('results', [])
        logger.info(f"Successfully fetched {len(projects)} projects")
        
        # Convert to more manageable format
        formatted_projects = []
        for project in projects:
            formatted_project = {
                'id': project['id'],
                'title': project['properties'].get('Name', {}).get('title', [{}])[0].get('plain_text', 'Untitled Project'),
                'status': project['properties'].get('Status', {}).get('status', {}).get('name', 'Not Started'),
                'priority': project['properties'].get('Priority', {}).get('select', {}).get('name', 'Medium'),
                'created_time': project['created_time'],
                'last_edited_time': project['last_edited_time'],
                'url': project['url']
            }
            formatted_projects.append(formatted_project)
        
        return formatted_projects
        
    except Exception as e:
        logger.error(f"Error fetching projects: {e}")
        raise

def get_tasks(notion, database_id):
    """
    Fetch tasks from Notion database.
    
    Args:
        notion: Initialized Notion client
        database_id: ID of the tasks database
        
    Returns:
        List of task objects
    """
    try:
        logger.info(f"Fetching tasks from database {database_id}")
        
        response = notion.databases.query(
            database_id=database_id,
            filter={
                "property": "Status",
                "status": {
                    "does_not_equal": "Completed"
                }
            },
            sorts=[
                {
                    "property": "Due Date",
                    "direction": "ascending"
                }
            ]
        )
        
        tasks = response.get('results', [])
        logger.info(f"Successfully fetched {len(tasks)} tasks")
        
        # Convert to more manageable format
        formatted_tasks = []
        for task in tasks:
            # Extract due date if available
            due_date = None
            due_date_prop = task['properties'].get('Due Date', {}).get('date', {})
            if due_date_prop:
                due_date = due_date_prop.get('start')
            
            # Extract project relation if available
            project_id = None
            project_relation = task['properties'].get('Project', {}).get('relation', [])
            if project_relation:
                project_id = project_relation[0].get('id')
            
            formatted_task = {
                'id': task['id'],
                'title': task['properties'].get('Name', {}).get('title', [{}])[0].get('plain_text', 'Untitled Task'),
                'status': task['properties'].get('Status', {}).get('status', {}).get('name', 'Not Started'),
                'due_date': due_date,
                'project_id': project_id,
                'created_time': task['created_time'],
                'last_edited_time': task['last_edited_time'],
                'url': task['url']
            }
            formatted_tasks.append(formatted_task)
        
        return formatted_tasks
        
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise

def get_prompt_library(notion, database_id):
    """
    Fetch prompts from the Notion prompt library.
    
    Args:
        notion: Initialized Notion client
        database_id: ID of the prompts database
        
    Returns:
        List of prompt objects
    """
    try:
        logger.info(f"Fetching prompts from database {database_id}")
        
        response = notion.databases.query(
            database_id=database_id,
            sorts=[
                {
                    "property": "Category",
                    "direction": "ascending"
                }
            ]
        )
        
        prompts = response.get('results', [])
        logger.info(f"Successfully fetched {len(prompts)} prompts")
        
        # Convert to more manageable format
        formatted_prompts = []
        for prompt in prompts:
            # Extract category
            category = prompt['properties'].get('Category', {}).get('select', {}).get('name', 'Uncategorized')
            
            # Extract tags
            tags = []
            tags_multi_select = prompt['properties'].get('Tags', {}).get('multi_select', [])
            if tags_multi_select:
                tags = [tag.get('name') for tag in tags_multi_select]
            
            # Extract prompt text from rich text property
            prompt_text = ""
            rich_text_blocks = prompt['properties'].get('Prompt Text', {}).get('rich_text', [])
            for block in rich_text_blocks:
                prompt_text += block.get('plain_text', '')
            
            formatted_prompt = {
                'id': prompt['id'],
                'title': prompt['properties'].get('Name', {}).get('title', [{}])[0].get('plain_text', 'Untitled Prompt'),
                'category': category,
                'tags': tags,
                'prompt_text': prompt_text,
                'created_time': prompt['created_time'],
                'last_edited_time': prompt['last_edited_time'],
                'url': prompt['url']
            }
            formatted_prompts.append(formatted_prompt)
        
        return formatted_prompts
        
    except Exception as e:
        logger.error(f"Error fetching prompts: {e}")
        raise
