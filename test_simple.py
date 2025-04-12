# test_simple.py
from notion_client import Client

def test_connection():
    # Your Notion API key
    api_key = "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"
    
    print("Initializing Notion client...")
    notion = Client(auth=api_key)
    
    print("Testing API connection...")
    user = notion.users.me()
    print(f"Connection successful! Logged in as: {user.get('name', 'Unknown')}")
    
    return True

if __name__ == "__main__":
    test_connection()