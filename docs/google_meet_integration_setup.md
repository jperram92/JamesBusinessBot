# Google Meet Integration Setup Process

## Overview

This document outlines the process for setting up Google Meet integration for the Business Meeting Assistant Bot. The integration allows the bot to create calendar events with Google Meet links, enabling seamless scheduling of virtual meetings.

## Prerequisites

- Google Cloud Platform account
- Google Workspace account (for domain-wide delegation)
- Python 3.7+ installed
- Required Python packages:
  - google-auth
  - google-auth-oauthlib
  - google-auth-httplib2
  - google-api-python-client
  - python-dotenv

## Setup Process

### 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com)
2. Click on the project dropdown at the top of the page
3. Click "New Project"
4. Enter a project name (e.g., "Business Meeting Assistant")
5. Click "Create"

### 2. Enable Required APIs

1. In the Google Cloud Console, navigate to "APIs & Services" > "Library"
2. Search for and enable the following APIs:
   - Google Calendar API
   - Google Meet API
   - Google Drive API (for saving transcripts)
   - Google People API (for user information)

### 3. Create Service Account Credentials

1. In the Google Cloud Console, navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Enter a service account name (e.g., "meeting-assistant-bot")
4. Click "Create and Continue"
5. For the role, select "Project" > "Editor" (or "Owner" for full access)
6. Click "Continue" and then "Done"
7. Find your newly created service account in the list and click on it
8. Go to the "Keys" tab
9. Click "Add Key" > "Create new key"
10. Choose "JSON" format
11. Click "Create" to download the key file
12. Save the key file as `google-credentials.json` in the `secrets` directory of your project

### 4. Configure Service Account Permissions

1. In the Google Cloud Console, navigate to "IAM & Admin" > "IAM"
2. Find your service account in the list
3. Click the edit (pencil) icon
4. Click "ADD ANOTHER ROLE"
5. Add the following roles:
   - Calendar API > Calendar Admin
   - Meet API > Meet Admin
6. Click "SAVE"

### 5. Enable Domain-Wide Delegation (for Google Workspace)

1. Go to your Google Workspace Admin Console
2. Navigate to Security > API Controls
3. Under "Domain-wide delegation", add your service account's client ID
4. Add the following OAuth scopes:
   ```
   https://www.googleapis.com/auth/calendar
   https://www.googleapis.com/auth/calendar.events
   https://www.googleapis.com/auth/meetings.space.created
   ```

### 6. Configure Environment Variables

1. Create a `.env` file in the root directory of your project
2. Add the following environment variables:
   ```
   GOOGLE_CREDENTIALS_PATH=secrets/google-credentials.json
   ```

## Testing the Integration

To test the Google Meet integration, run the following command:

```bash
python src/tests/test_google_meet.py
```

This script will:
1. Load the service account credentials
2. Create a test calendar event
3. Attempt to add a Google Meet link to the event
4. Display the results, including the meeting ID, start time, end time, and Meet link (if successful)

## Troubleshooting

### Common Issues

1. **"Google credentials file not found!"**
   - Ensure that the `google-credentials.json` file exists in the `secrets` directory
   - Check that the `GOOGLE_CREDENTIALS_PATH` environment variable is set correctly

2. **"Invalid conference type value"**
   - This error occurs when trying to create a Meet link with an incorrect conference type
   - Try using `eventHangout` instead of `hangoutsMeet` as the conference type
   - Ensure that the Google Meet API is enabled for your project

3. **"API has not been used in project before or is disabled"**
   - This error occurs when the Google Calendar API or Google Meet API is not enabled
   - Go to the Google Cloud Console and enable the required APIs

4. **Meet link not generated**
   - Ensure that the service account has the necessary permissions (Calendar Admin and Meet Admin roles)
   - Check that domain-wide delegation is properly configured
   - Verify that the OAuth scopes are correctly set

### Debugging Tips

1. Enable verbose logging by adding the following code to your script:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. Check the service account permissions in the Google Cloud Console
3. Verify that the APIs are enabled and that there are no quota issues
4. Test creating a regular calendar event without a Meet link to isolate the issue

## Code Example

Here's a simplified example of how to create a calendar event with a Google Meet link:

```python
import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_meeting_with_meet_link(summary, description, start_time, end_time):
    """Create a calendar event with a Google Meet link."""
    # Load credentials
    credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=[
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/meetings.space.created'
        ]
    )

    # Build the Calendar service
    service = build('calendar', 'v3', credentials=credentials)

    # Create the event
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat() + 'Z',
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time.isoformat() + 'Z',
            'timeZone': 'UTC',
        },
        'conferenceData': {
            'createRequest': {
                'requestId': f'meeting-{start_time.strftime("%Y%m%d-%H%M%S")}',
                'conferenceSolutionKey': {
                    'type': 'eventHangout'
                }
            }
        }
    }

    # Insert the event
    event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1
    ).execute()

    return event

# Example usage
start_time = datetime.utcnow() + timedelta(hours=1)
end_time = start_time + timedelta(hours=1)
event = create_meeting_with_meet_link(
    'Test Meeting',
    'This is a test meeting',
    start_time,
    end_time
)
print(f"Meeting created: {event['id']}")
print(f"Meet link: {event.get('hangoutLink', 'No meet link generated')}")
```

## Conclusion

Setting up Google Meet integration for the Business Meeting Assistant Bot involves several steps, including creating a Google Cloud project, enabling the necessary APIs, creating and configuring a service account, and testing the integration. By following the steps outlined in this document, you should be able to successfully integrate Google Meet with your bot and create calendar events with Meet links.

If you encounter any issues during the setup process, refer to the troubleshooting section for guidance on resolving common problems. 