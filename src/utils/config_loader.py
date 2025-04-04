import os
import yaml
from typing import Dict

def load_config(config_path: str) -> Dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Validate required configuration sections
        required_sections = ['bot', 'meetings', 'openai', 'jira', 'documents', 'logging']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required configuration section: {section}")
                
        # Validate environment variables
        required_env_vars = [
            'OPENAI_API_KEY',
            'JIRA_API_TOKEN',
            'JIRA_EMAIL',
            'JIRA_URL'
        ]
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
            
        return config
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing configuration file: {str(e)}")
    except Exception as e:
        raise Exception(f"Error loading configuration: {str(e)}")
        
def validate_meeting_config(config: Dict) -> bool:
    """Validate meeting-specific configuration."""
    try:
        meetings_config = config['meetings']
        
        # Check if at least one meeting platform is enabled
        if not (meetings_config['teams']['enabled'] or meetings_config['google_meet']['enabled']):
            raise ValueError("At least one meeting platform must be enabled")
            
        # Validate Teams configuration if enabled
        if meetings_config['teams']['enabled']:
            if not os.getenv('TEAMS_APP_ID') or not os.getenv('TEAMS_APP_PASSWORD'):
                raise ValueError("Teams credentials not configured")
                
        # Validate Google Meet configuration if enabled
        if meetings_config['google_meet']['enabled']:
            if not os.getenv('GOOGLE_MEET_CREDENTIALS'):
                raise ValueError("Google Meet credentials not configured")
                
        return True
        
    except Exception as e:
        raise ValueError(f"Invalid meeting configuration: {str(e)}")
        
def validate_document_config(config: Dict) -> bool:
    """Validate document generation configuration."""
    try:
        docs_config = config['documents']
        
        # Check if output directories exist or can be created
        for doc_type in ['word', 'powerpoint']:
            output_dir = docs_config[doc_type]['output_dir']
            os.makedirs(output_dir, exist_ok=True)
            
        # Check if template files exist
        for doc_type in ['word', 'powerpoint']:
            template_path = docs_config[doc_type]['template_path']
            if not os.path.exists(template_path):
                raise ValueError(f"Template file not found: {template_path}")
                
        return True
        
    except Exception as e:
        raise ValueError(f"Invalid document configuration: {str(e)}")
        
def get_logging_config(config: Dict) -> Dict:
    """Extract and validate logging configuration."""
    try:
        logging_config = config['logging']
        
        # Ensure log directory exists
        log_dir = os.path.dirname(logging_config['file'])
        os.makedirs(log_dir, exist_ok=True)
        
        return {
            'level': logging_config['level'],
            'filename': logging_config['file'],
            'maxBytes': logging_config['max_size'],
            'backupCount': logging_config['backup_count']
        }
        
    except Exception as e:
        raise ValueError(f"Invalid logging configuration: {str(e)}") 