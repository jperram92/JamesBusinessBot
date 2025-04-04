import os
import sys
import logging
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the EmailNotifier class
from utils.email_notifier import EmailNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_google_meet_connection():
    """Test the Google Meet integration by creating a test meeting."""
    try:
        # Set up credentials
        credentials_path = os.path.join('secrets', 'google-credentials.json')
        logger.info(f"Looking for credentials at: {credentials_path}")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Absolute path to credentials: {os.path.abspath(credentials_path)}")
        
        if not os.path.exists(credentials_path):
            logger.error(f"Credentials file not found at {credentials_path}")
            return False
            
        logger.info("Credentials file found, loading...")
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        # Build the Calendar service
        logger.info("Building Calendar service...")
        service = build('calendar', 'v3', credentials=credentials)
        
        # Create a test meeting
        logger.info("Creating calendar event...")
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=1)
        
        event = {
            'summary': 'Test Meeting - Business Meeting Assistant',
            'description': 'This is a test meeting created by the Business Meeting Assistant Bot',
            'start': {
                'dateTime': start_time.isoformat() + 'Z',
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat() + 'Z',
                'timeZone': 'UTC',
            }
        }
        
        # Create the event
        event = service.events().insert(calendarId='primary', body=event).execute()
        
        # Log meeting details
        logger.info("Test successful! Meeting created:")
        logger.info(f"Meeting ID: {event['id']}")
        logger.info(f"Start Time: {event['start']['dateTime']}")
        logger.info(f"End Time: {event['end']['dateTime']}")
        
        logger.info("\nMeeting Details:")
        logger.info(f"Title: {event['summary']}")
        logger.info(f"Description: {event['description']}")
        logger.info(f"Start Time: {event['start']['dateTime']}")
        logger.info(f"End Time: {event['end']['dateTime']}")
        
        # Send email notification
        try:
            email_notifier = EmailNotifier()
            meeting_details = {
                'title': event['summary'],
                'description': event['description'],
                'start_time': event['start']['dateTime'],
                'end_time': event['end']['dateTime'],
                'meet_link': event.get('hangoutLink', 'No meet link generated')
            }
            
            # Get recipient email from environment variable
            recipient_email = os.getenv('RECIPIENT_EMAIL')
            if not recipient_email:
                logger.error("RECIPIENT_EMAIL not set in environment variables")
                return False
                
            if email_notifier.send_meeting_invitation(recipient_email, meeting_details):
                logger.info(f"Email invitation sent successfully to {recipient_email}")
            else:
                logger.error("Failed to send email invitation")
                
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            logger.error("\nFailed to send email invitation")
        
        return True
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_google_meet_connection() 