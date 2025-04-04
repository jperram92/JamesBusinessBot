import os
import pytest
import asyncio
from unittest.mock import MagicMock, patch
from src.bot.meeting_bot import MeetingBot
from src.utils.config_loader import load_config

# Mock configuration
MOCK_CONFIG = {
    'bot': {
        'name': 'Test Bot',
        'email_domain': 'test.com',
        'language': 'en-US'
    },
    'meetings': {
        'teams': {
            'enabled': True,
            'auto_join': True,
            'record_audio': True
        },
        'google_meet': {
            'enabled': True,
            'auto_join': True,
            'record_audio': True
        }
    },
    'openai': {
        'model': 'gpt-4',
        'temperature': 0.7,
        'max_tokens': 2000,
        'summary_prompt': 'Test prompt'
    },
    'jira': {
        'default_project': 'TEST',
        'ticket_template': 'Test template'
    },
    'documents': {
        'word': {
            'template_path': 'templates/test.docx',
            'output_dir': 'output/word'
        },
        'powerpoint': {
            'template_path': 'templates/test.pptx',
            'output_dir': 'output/powerpoint'
        }
    },
    'logging': {
        'level': 'INFO',
        'file': 'logs/test.log',
        'max_size': 10485760,
        'backup_count': 5
    }
}

@pytest.fixture
def mock_env_vars():
    """Set up mock environment variables."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_openai_key',
        'JIRA_API_TOKEN': 'test_jira_token',
        'JIRA_EMAIL': 'test@example.com',
        'JIRA_URL': 'https://test.atlassian.net',
        'TEAMS_APP_ID': 'test_teams_id',
        'TEAMS_APP_PASSWORD': 'test_teams_password',
        'GOOGLE_MEET_CREDENTIALS': 'test_credentials.json'
    }):
        yield

@pytest.fixture
def mock_config_loader():
    """Mock the config loader."""
    with patch('src.utils.config_loader.load_config', return_value=MOCK_CONFIG):
        yield

@pytest.fixture
def meeting_bot(mock_env_vars, mock_config_loader):
    """Create a MeetingBot instance with mocked dependencies."""
    with patch('src.services.teams_service.TeamsService') as mock_teams, \
         patch('src.services.google_meet_service.GoogleMeetService') as mock_google, \
         patch('src.services.openai_service.OpenAIService') as mock_openai, \
         patch('src.services.jira_service.JiraService') as mock_jira, \
         patch('src.services.document_service.DocumentService') as mock_doc:
        
        # Set up mock services
        mock_teams.return_value.join_meeting.return_value = True
        mock_google.return_value.join_meeting.return_value = True
        mock_openai.return_value.transcribe_audio.return_value = "Test transcription"
        mock_openai.return_value.generate_summary.return_value = "Test summary"
        mock_jira.return_value.update_ticket.return_value = True
        mock_doc.return_value.create_word_document.return_value = "test.docx"
        mock_doc.return_value.create_powerpoint.return_value = "test.pptx"
        
        bot = MeetingBot()
        yield bot

@pytest.mark.asyncio
async def test_join_meeting_teams(meeting_bot):
    """Test joining a Teams meeting."""
    result = await meeting_bot.join_meeting("test-meeting-id", "teams")
    assert result is True
    assert meeting_bot.current_meeting is not None

@pytest.mark.asyncio
async def test_join_meeting_google(meeting_bot):
    """Test joining a Google Meet meeting."""
    result = await meeting_bot.join_meeting("test-meeting-id", "google")
    assert result is True
    assert meeting_bot.current_meeting is not None

@pytest.mark.asyncio
async def test_process_audio(meeting_bot):
    """Test processing audio data."""
    await meeting_bot.process_audio(b"test audio data")
    assert len(meeting_bot.transcription_buffer) > 0

@pytest.mark.asyncio
async def test_process_transcription_buffer(meeting_bot):
    """Test processing transcription buffer."""
    meeting_bot.transcription_buffer = ["Test 1", "Test 2", "Test 3"]
    summary = await meeting_bot.process_transcription_buffer()
    assert summary == "Test summary"
    assert len(meeting_bot.transcription_buffer) == 0

@pytest.mark.asyncio
async def test_update_jira_ticket(meeting_bot):
    """Test updating a JIRA ticket."""
    result = await meeting_bot.update_jira_ticket(
        "TEST-123",
        "Test Summary",
        "Test Description"
    )
    assert result is True

@pytest.mark.asyncio
async def test_generate_documents(meeting_bot):
    """Test generating documents."""
    docs = await meeting_bot.generate_documents("test-meeting-id", "Test content")
    assert docs is not None
    assert "word" in docs
    assert "powerpoint" in docs

@pytest.mark.asyncio
async def test_leave_meeting(meeting_bot):
    """Test leaving a meeting."""
    meeting_bot.current_meeting = "test-meeting"
    result = await meeting_bot.leave_meeting()
    assert result is True
    assert meeting_bot.current_meeting is None 