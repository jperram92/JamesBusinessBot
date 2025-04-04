import os
import sys
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

def test_google_meet_connection():
    """Test the Google Meet integration by creating a test meeting."""
    try:
        # Load credentials
        credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
        print(f"\nLooking for credentials at: {credentials_path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Absolute path to credentials: {os.path.abspath(credentials_path)}")

        if not credentials_path or not os.path.exists(credentials_path):
            print("Error: Google credentials file not found!")
            return False

        print("Found credentials file, attempting to load...")
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=[
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/calendar.events',
                'https://www.googleapis.com/auth/meetings.space.created',
                'https://www.googleapis.com/auth/calendar.readonly'
            ]
        )

        print("Credentials loaded successfully, building Calendar service...")
        # Build the Calendar service
        calendar_service = build('calendar', 'v3', credentials=credentials)

        # Create a test meeting
        start_time = datetime.utcnow() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        # Create a regular calendar event
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
            },
            'attendees': [
                {'email': 'your.email@example.com'},  # Replace with your email address
            ],
            'conferenceData': {
                'createRequest': {
                    'requestId': f'test-meeting-{start_time.strftime("%Y%m%d-%H%M%S")}',
                    'conferenceSolutionKey': {
                        'type': 'eventHangout'
                    }
                }
            }
        }

        print("Creating calendar event...")
        try:
            event = calendar_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            print("\nTest successful! Meeting created:")
            print(f"Meeting ID: {event['id']}")
            print(f"Start Time: {event['start']['dateTime']}")
            print(f"End Time: {event['end']['dateTime']}")

            return True

        except Exception as e:
            print(f"\nError creating meeting: {str(e)}")
            print("\nDetailed error information:")
            if hasattr(e, 'content'):
                import json
                try:
                    error_details = json.loads(e.content.decode('utf-8'))
                    print(json.dumps(error_details, indent=2))
                except:
                    print(e.content)

            return False

    except Exception as e:
        print(f"\nError testing Google Meet integration: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Google Meet integration...")
    test_google_meet_connection() 