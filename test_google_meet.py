import asyncio
import yaml
from src.services.google_meet_service import GoogleMeetService

async def test_google_meet():
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize Google Meet service
    meet_service = GoogleMeetService(config)
    
    # Test joining a meeting using the code from the URL
    meeting_code = "sgf-euot-epd"  # Code from https://meet.google.com/sgf-euot-epd
    try:
        await meet_service.join_meeting(meeting_code)
        print(f"Successfully joined meeting with code: {meeting_code}")
        
        # Stay in the meeting for 2 minutes
        print("Staying in the meeting for 2 minutes...")
        await asyncio.sleep(120)
        
        # Leave the meeting
        await meet_service.leave_meeting()
        print("Successfully left the meeting")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_google_meet()) 