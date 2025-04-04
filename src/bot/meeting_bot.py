import asyncio
import logging
from typing import Dict, List, Optional, Union

from ..services.document_service import DocumentService
from ..services.google_meet_service import GoogleMeetService
from ..services.jira_service import JiraService
from ..services.openai_service import OpenAIService
from ..services.teams_service import TeamsService

logger = logging.getLogger(__name__)

class MeetingBot:
    """Core bot functionality that orchestrates various services."""
    
    def __init__(self, config: Dict):
        """Initialize the meeting bot with configuration."""
        self.config = config
        self.current_meeting = None
        self.transcription_buffer = []
        self.summary = None
        self.action_items = []
        self.key_points = []
        self.next_steps = []
        
        # Initialize services
        self.teams_service = TeamsService(self.config) if self.config['meetings']['teams']['enabled'] else None
        self.google_meet_service = GoogleMeetService(self.config) if self.config['meetings']['google_meet']['enabled'] else None
        self.openai_service = OpenAIService(self.config)
        self.jira_service = JiraService(self.config)
        self.document_service = DocumentService(self.config)
        
        logger.info("Meeting bot initialized with configuration")
    
    async def join_meeting(self, meeting_id: str, platform: str = "teams", title: Optional[str] = None, description: Optional[str] = None) -> bool:
        """Join a meeting on the specified platform."""
        try:
            if platform.lower() == "teams" and self.teams_service:
                self.current_meeting = await self.teams_service.join_meeting(meeting_id)
            elif platform.lower() == "google" and self.google_meet_service:
                self.current_meeting = await self.google_meet_service.join_meeting(meeting_id)
            else:
                logger.error(f"Unsupported platform: {platform}")
                return False
            
            logger.info(f"Successfully joined {platform} meeting: {meeting_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to join meeting: {str(e)}")
            return False
    
    async def leave_meeting(self, meeting_id: str) -> bool:
        """Leave the current meeting."""
        try:
            if self.current_meeting:
                if isinstance(self.current_meeting, TeamsService):
                    await self.teams_service.leave_meeting()
                elif isinstance(self.current_meeting, GoogleMeetService):
                    await self.google_meet_service.leave_meeting()
                
                self.current_meeting = None
                logger.info("Successfully left the meeting")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to leave meeting: {str(e)}")
            return False
    
    async def process_meeting(self, meeting_id: str) -> None:
        """Process the meeting in the background."""
        try:
            while self.current_meeting:
                # Process audio data if available
                if self.transcription_buffer:
                    await self._process_transcription_buffer()
                await asyncio.sleep(1)  # Avoid busy waiting
        except Exception as e:
            logger.error(f"Error processing meeting: {str(e)}")
    
    async def _process_transcription_buffer(self) -> None:
        """Process the transcription buffer and generate summaries."""
        try:
            # Convert audio buffer to text
            text = await self.openai_service.transcribe_audio(b"".join(self.transcription_buffer))
            
            # Generate summary and extract information
            summary_data = await self.openai_service.generate_summary(text)
            
            # Update bot state
            self.summary = summary_data['summary']
            self.action_items.extend(summary_data['action_items'])
            self.key_points.extend(summary_data['key_points'])
            self.next_steps.extend(summary_data['next_steps'])
            
            # Clear the buffer
            self.transcription_buffer = []
            
            logger.info("Successfully processed transcription buffer")
        except Exception as e:
            logger.error(f"Failed to process transcription buffer: {str(e)}")
    
    async def generate_document(self, meeting_id: str, doc_type: str = "summary", format: str = "docx") -> str:
        """Generate documents from meeting content."""
        try:
            # Prepare document data
            doc_data = {
                'meeting_id': meeting_id,
                'summary': self.summary,
                'key_points': self.key_points,
                'action_items': self.action_items,
                'next_steps': self.next_steps
            }
            
            # Generate document
            if format.lower() == "docx":
                doc_path = await self.document_service.create_word_document(meeting_id, doc_data)
            elif format.lower() == "pptx":
                doc_path = await self.document_service.create_powerpoint_presentation(meeting_id, doc_data)
            else:
                raise ValueError(f"Unsupported document format: {format}")
            
            logger.info(f"Successfully generated {format} document: {doc_path}")
            return doc_path
        except Exception as e:
            logger.error(f"Failed to generate document: {str(e)}")
            raise
    
    async def create_action_items(self, meeting_id: str, action_items: List[Dict]) -> List[str]:
        """Create JIRA tickets for action items."""
        try:
            ticket_ids = []
            for item in action_items:
                ticket_id = await self.jira_service.create_ticket(
                    summary=item['description'],
                    description=f"Action item from meeting {meeting_id}",
                    assignee=item.get('assignee'),
                    due_date=item.get('due_date')
                )
                ticket_ids.append(ticket_id)
            return ticket_ids
        except Exception as e:
            logger.error(f"Failed to create action items: {str(e)}")
            raise
    
    async def update_meeting_ticket(self, meeting_id: str, summary: Optional[str] = None, description: Optional[str] = None) -> bool:
        """Update the JIRA ticket for the meeting."""
        try:
            success = await self.jira_service.update_ticket(
                ticket_id=meeting_id,
                summary=summary,
                description=description
            )
            return success
        except Exception as e:
            logger.error(f"Failed to update meeting ticket: {str(e)}")
            raise
    
    async def get_meeting_status(self, meeting_id: str) -> Dict[str, Union[str, List[str]]]:
        """Get the current status of the meeting."""
        return {
            'meeting_id': meeting_id,
            'platform': self.current_meeting.__class__.__name__ if self.current_meeting else None,
            'summary': self.summary,
            'action_items': [item['description'] for item in self.action_items],
            'key_points': self.key_points,
            'next_steps': self.next_steps
        } 