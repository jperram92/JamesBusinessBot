import os
import yaml
from dotenv import load_dotenv

def load_config(config_path: str = "src/config/config.yaml") -> dict:
    """Load configuration from config file and environment variables."""
    # Load environment variables
    load_dotenv()
    
    # Load config file
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        config = {}
    
    # Override with environment variables
    config.setdefault('openai', {})['api_key'] = os.getenv('OPENAI_API_KEY')
    
    config.setdefault('jira', {}).update({
        'server': os.getenv('JIRA_SERVER'),
        'username': os.getenv('JIRA_USERNAME'),
        'api_token': os.getenv('JIRA_API_TOKEN'),
        'project_key': os.getenv('JIRA_PROJECT_KEY')
    })
    
    config.setdefault('google_meet', {})['credentials_path'] = os.getenv('GOOGLE_CREDENTIALS_PATH')
    
    config.setdefault('logging', {}).update({
        'level': os.getenv('LOG_LEVEL', 'INFO'),
        'file': os.getenv('LOG_FILE', 'logs/meeting-bot.log')
    })
    
    return config 