import asyncio
import logging
from typing import Dict, Optional

from botframework.connector import ConnectorClient
from botframework.schema import Activity
from botframework.streaming import StreamingHttpClient
from botframework.streaming.transport import WebSocketTransport

logger = logging.getLogger(__name__)

class TeamsService:
    """Microsoft Teams meeting service implementation."""
    
    def __init__(self, config: Dict):
        """Initialize the Teams service with configuration."""
        self.config = config
        self.app_id = config['teams']['app_id']
        self.app_password = config['teams']['app_password']
        self.connector_client = None
        self.current_meeting = None
        self.audio_stream = None
        
        logger.info("Teams service initialized")
    
    async def join_meeting(self, meeting_id: str) -> bool:
        """Join a Teams meeting."""
        try:
            # Initialize Teams client
            self.connector_client = ConnectorClient(
                app_id=self.app_id,
                app_password=self.app_password
            )
            
            # Join the meeting
            join_url = f"https://teams.microsoft.com/l/meetup-join/{meeting_id}"
            self.current_meeting = await self.connector_client.conversations.create_conversation(
                activity=Activity(
                    type="event",
                    name="JoinMeeting",
                    value={"joinUrl": join_url}
                )
            )
            
            # Start audio capture
            await self._start_audio_capture()
            
            logger.info(f"Successfully joined Teams meeting: {meeting_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to join Teams meeting: {str(e)}")
            return False
    
    async def leave_meeting(self) -> bool:
        """Leave the current Teams meeting."""
        try:
            if self.current_meeting:
                # Stop audio capture
                await self._stop_audio_capture()
                
                # Leave the meeting
                await self.connector_client.conversations.delete_conversation(
                    self.current_meeting.id
                )
                
                self.current_meeting = None
                self.audio_stream = None
                
                logger.info("Successfully left Teams meeting")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to leave Teams meeting: {str(e)}")
            return False
    
    async def _start_audio_capture(self) -> None:
        """Start capturing audio from the Teams meeting."""
        try:
            # Initialize streaming client
            transport = WebSocketTransport()
            streaming_client = StreamingHttpClient(transport)
            
            # Start audio stream
            self.audio_stream = await streaming_client.start_stream(
                self.current_meeting.id,
                "audio"
            )
            
            # Start audio capture loop
            asyncio.create_task(self._audio_capture_loop())
            
            logger.info("Started audio capture for Teams meeting")
        except Exception as e:
            logger.error(f"Failed to start audio capture: {str(e)}")
            raise
    
    async def _stop_audio_capture(self) -> None:
        """Stop capturing audio from the Teams meeting."""
        try:
            if self.audio_stream:
                await self.audio_stream.stop()
                self.audio_stream = None
                logger.info("Stopped audio capture for Teams meeting")
        except Exception as e:
            logger.error(f"Failed to stop audio capture: {str(e)}")
            raise
    
    async def _audio_capture_loop(self) -> None:
        """Main loop for capturing audio data."""
        try:
            while self.audio_stream and self.audio_stream.is_active:
                # Read audio data
                audio_data = await self.audio_stream.read()
                
                # Process audio data
                if audio_data:
                    # Convert to bytes if needed
                    if isinstance(audio_data, str):
                        audio_data = audio_data.encode('utf-8')
                    
                    # Yield audio data for processing
                    yield audio_data
                
                # Small delay to prevent CPU overload
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in audio capture loop: {str(e)}")
            raise
    
    @property
    def meeting_id(self) -> Optional[str]:
        """Get the current meeting ID."""
        return self.current_meeting.id if self.current_meeting else None 