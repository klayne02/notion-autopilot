from notion.updater import load_config, initialize_notion_client

def test_connection():
    print("Loading configuration...")
    config = load_config()
    
    print("Initializing Notion client...")
    notion = initialize_notion_client(config)
    
    print("Testing API connection...")
    user = notion.users.me()
    print(f"Connection successful! Logged in as: {user['name']}")
    
    return True

if __name__ == "__main__":
    test_connection()