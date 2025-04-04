import logging
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

from src.bot.meeting_bot import MeetingBot
from src.config.config_loader import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Business Meeting Assistant Bot",
    description="API for managing meeting assistance, transcription, and documentation",
    version="1.0.0"
)

# Load configuration
config = load_config()

# Initialize meeting bot
meeting_bot = MeetingBot(config)

# Pydantic models for request/response validation
class MeetingRequest(BaseModel):
    meeting_id: str
    platform: str
    title: Optional[str] = None
    description: Optional[str] = None

class DocumentRequest(BaseModel):
    meeting_id: str
    document_type: str
    format: str = "docx"

class ActionItem(BaseModel):
    description: str
    assignee: Optional[str] = None
    due_date: Optional[str] = None

class JiraUpdateRequest(BaseModel):
    meeting_id: str
    action_items: List[ActionItem]
    summary: Optional[str] = None
    description: Optional[str] = None

@app.post("/meetings/join")
async def join_meeting(request: MeetingRequest, background_tasks: BackgroundTasks):
    """Join a meeting on the specified platform."""
    try:
        success = await meeting_bot.join_meeting(
            meeting_id=request.meeting_id,
            platform=request.platform,
            title=request.title,
            description=request.description
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to join meeting")
        
        # Start processing in background
        background_tasks.add_task(meeting_bot.process_meeting, request.meeting_id)
        
        return {"status": "success", "message": f"Joined meeting {request.meeting_id}"}
        
    except Exception as e:
        logger.error(f"Error joining meeting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/meetings/leave")
async def leave_meeting(meeting_id: str):
    """Leave a meeting."""
    try:
        success = await meeting_bot.leave_meeting(meeting_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to leave meeting")
        
        return {"status": "success", "message": f"Left meeting {meeting_id}"}
        
    except Exception as e:
        logger.error(f"Error leaving meeting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/generate")
async def generate_document(request: DocumentRequest):
    """Generate a document for a meeting."""
    try:
        filepath = await meeting_bot.generate_document(
            meeting_id=request.meeting_id,
            doc_type=request.document_type,
            format=request.format
        )
        
        return {
            "status": "success",
            "message": "Document generated successfully",
            "filepath": filepath
        }
        
    except Exception as e:
        logger.error(f"Error generating document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/jira/update")
async def update_jira(request: JiraUpdateRequest):
    """Update JIRA with meeting information and action items."""
    try:
        # Create action items
        action_item_tickets = await meeting_bot.create_action_items(
            meeting_id=request.meeting_id,
            action_items=[item.dict() for item in request.action_items]
        )
        
        # Update meeting ticket if summary/description provided
        if request.summary or request.description:
            await meeting_bot.update_meeting_ticket(
                meeting_id=request.meeting_id,
                summary=request.summary,
                description=request.description
            )
        
        return {
            "status": "success",
            "message": "JIRA updated successfully",
            "action_item_tickets": action_item_tickets
        }
        
    except Exception as e:
        logger.error(f"Error updating JIRA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meetings/{meeting_id}/status")
async def get_meeting_status(meeting_id: str):
    """Get the current status of a meeting."""
    try:
        status = await meeting_bot.get_meeting_status(meeting_id)
        return status
        
    except Exception as e:
        logger.error(f"Error getting meeting status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 