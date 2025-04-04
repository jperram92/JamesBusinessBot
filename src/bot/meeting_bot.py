import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Union

from ..services.document_service import DocumentService
from ..services.google_meet_service import GoogleMeetService
from ..services.jira_service import JiraService
from ..services.openai_service import OpenAIService
from ..services.teams_service import TeamsService
from ..utils.config_loader import ConfigLoader

logger = logging.getLogger(__name__)

class MeetingBot:
    """Core bot functionality that orchestrates various services."""
    
    def __init__(self, config_path: str = "src/config/config.yaml"):
        """Initialize the meeting bot with configuration."""
        self.config = ConfigLoader.load_config(config_path)
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
    
    async def join_meeting(self, meeting_id: str, platform: str = "teams") -> bool:
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
    
    async def leave_meeting(self) -> bool:
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
    
    async def process_audio(self, audio_data: bytes) -> None:
        """Process audio data from the meeting."""
        try:
            # Add audio data to transcription buffer
            self.transcription_buffer.append(audio_data)
            
            # Process buffer when it reaches a certain size
            if len(self.transcription_buffer) >= self.config['transcription']['buffer_size']:
                await self._process_transcription_buffer()
        except Exception as e:
            logger.error(f"Failed to process audio: {str(e)}")
    
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
    
    async def generate_documents(self, meeting_id: str, format: str = "word") -> str:
        """Generate documents from meeting content."""
        try:
            # Prepare document data
            doc_data = {
                'meeting_id': meeting_id,
                'meeting_date': datetime.now().strftime("%Y-%m-%d"),
                'meeting_time': datetime.now().strftime("%H:%M"),
                'platform': self.current_meeting.__class__.__name__,
                'summary': self.summary,
                'key_points': self.key_points,
                'action_items': self.action_items,
                'next_steps': self.next_steps,
                'notes': "\n".join(self.transcription_buffer)
            }
            
            # Generate document
            if format.lower() == "word":
                doc_path = await this.document_service.create_word_document(meeting_id, doc_data)
            elif format.lower() == "powerpoint":
                doc_path = await this.document_service.create_powerpoint_presentation(meeting_id, doc_data)
            else:
                raise ValueError(f"Unsupported document format: {format}")
            
            logger.info(f"Successfully generated {format} document: {doc_path}")
            return doc_path
        except Exception as e:
            logger.error(f"Failed to generate document: {str(e)}")
            raise
    
    async def update_jira(self, meeting_id: str, jira_ticket_id: str) -> bool:
        """Update JIRA ticket with meeting information."""
        try:
            # Prepare JIRA update data
            update_data = {
                'summary': self.summary,
                'action_items': self.action_items,
                'key_points': self.key_points,
                'next_steps': self.next_steps
            }
            
            # Update JIRA ticket
            success = await self.jira_service.update_ticket(jira_ticket_id, update_data)
            
            if success:
                logger.info(f"Successfully updated JIRA ticket: {jira_ticket_id}")
            else:
                logger.error(f"Failed to update JIRA ticket: {jira_ticket_id}")
            
            return success
        except Exception as e:
            logger.error(f"Failed to update JIRA: {str(e)}")
            return False
    
    def get_meeting_status(self) -> Dict[str, Union[str, List[str]]]:
        """Get the current status of the meeting."""
        return {
            'meeting_id': self.current_meeting.meeting_id if self.current_meeting else None,
            'platform': self.current_meeting.__class__.__name__ if self.current_meeting else None,
            'summary': self.summary,
            'action_items': [item['description'] for item in self.action_items],
            'key_points': self.key_points,
            'next_steps': self.next_steps
        } 