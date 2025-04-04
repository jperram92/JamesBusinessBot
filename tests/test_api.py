import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app

# Create a test client
client = TestClient(app)

# Mock the MeetingBot
@pytest.fixture
def mock_meeting_bot():
    with patch('src.main.bot') as mock_bot:
        # Set up mock methods
        mock_bot.join_meeting.return_value = True
        mock_bot.leave_meeting.return_value = True
        mock_bot.process_transcription_buffer.return_value = "Test summary"
        mock_bot.update_jira_ticket.return_value = True
        mock_bot.document_service.create_word_document.return_value = "test.docx"
        mock_bot.document_service.create_powerpoint.return_value = "test.pptx"
        mock_bot.generate_documents.return_value = {
            "word": "test.docx",
            "powerpoint": "test.pptx"
        }
        yield mock_bot

def test_join_meeting_teams(mock_meeting_bot):
    """Test joining a Teams meeting via API."""
    response = client.post(
        "/join-meeting",
        json={
            "meeting_id": "test-meeting-id",
            "platform": "teams"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Successfully joined meeting"}
    mock_meeting_bot.join_meeting.assert_called_once_with("test-meeting-id", "teams")

def test_join_meeting_google(mock_meeting_bot):
    """Test joining a Google Meet meeting via API."""
    response = client.post(
        "/join-meeting",
        json={
            "meeting_id": "test-meeting-id",
            "platform": "google"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Successfully joined meeting"}
    mock_meeting_bot.join_meeting.assert_called_once_with("test-meeting-id", "google")

def test_leave_meeting(mock_meeting_bot):
    """Test leaving a meeting via API."""
    response = client.post("/leave-meeting")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Successfully left meeting"}
    mock_meeting_bot.leave_meeting.assert_called_once()

def test_generate_documents_word(mock_meeting_bot):
    """Test generating a Word document via API."""
    response = client.post(
        "/generate-documents",
        json={
            "meeting_id": "test-meeting-id",
            "content": "Test content",
            "format": "word"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success", "document_path": "test.docx"}
    mock_meeting_bot.document_service.create_word_document.assert_called_once_with(
        "test-meeting-id", "Test content"
    )

def test_generate_documents_powerpoint(mock_meeting_bot):
    """Test generating a PowerPoint presentation via API."""
    response = client.post(
        "/generate-documents",
        json={
            "meeting_id": "test-meeting-id",
            "content": "Test content",
            "format": "powerpoint"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success", "document_path": "test.pptx"}
    mock_meeting_bot.document_service.create_powerpoint.assert_called_once_with(
        "test-meeting-id", "Test content"
    )

def test_generate_documents_both(mock_meeting_bot):
    """Test generating both document types via API."""
    response = client.post(
        "/generate-documents",
        json={
            "meeting_id": "test-meeting-id",
            "content": "Test content",
            "format": "both"
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "documents": {
            "word": "test.docx",
            "powerpoint": "test.pptx"
        }
    }
    mock_meeting_bot.generate_documents.assert_called_once_with(
        "test-meeting-id", "Test content"
    )

def test_update_jira(mock_meeting_bot):
    """Test updating a JIRA ticket via API."""
    response = client.post(
        "/update-jira",
        json={
            "meeting_id": "test-meeting-id",
            "jira_ticket_id": "TEST-123"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Successfully updated JIRA ticket"}
    mock_meeting_bot.process_transcription_buffer.assert_called_once()
    mock_meeting_bot.update_jira_ticket.assert_called_once_with(
        "TEST-123", "Meeting Summary - test-meeting-id", "Test summary"
    )

def test_update_jira_missing_ticket_id(mock_meeting_bot):
    """Test updating JIRA with missing ticket ID."""
    response = client.post(
        "/update-jira",
        json={
            "meeting_id": "test-meeting-id"
        }
    )
    assert response.status_code == 400
    assert "JIRA ticket ID is required" in response.json()["detail"] 