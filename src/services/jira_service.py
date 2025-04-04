import os
from typing import Dict, List, Optional
from jira import JIRA
import logging
from jira.exceptions import JIRAError

logger = logging.getLogger(__name__)

class JiraService:
    """JIRA integration service implementation."""
    
    def __init__(self, config: Dict):
        """Initialize the JIRA service with configuration."""
        self.config = config
        self.jira = JIRA(
            server=config['jira']['server'],
            basic_auth=(config['jira']['username'], config['jira']['api_token'])
        )
        self.project_key = config['jira']['project_key']
        logger.info("JIRA service initialized")
    
    async def create_ticket(self, summary: str, description: str, issue_type: str = "Task") -> str:
        """Create a new JIRA ticket."""
        try:
            issue_dict = {
                'project': self.project_key,
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type},
            }
            
            new_issue = self.jira.create_issue(fields=issue_dict)
            logger.info(f"Created JIRA ticket: {new_issue.key}")
            return new_issue.key
            
        except JIRAError as e:
            logger.error(f"Failed to create JIRA ticket: {str(e)}")
            raise
    
    async def update_ticket(self, issue_key: str, updates: Dict) -> None:
        """Update an existing JIRA ticket."""
        try:
            issue = self.jira.issue(issue_key)
            issue.update(fields=updates)
            logger.info(f"Updated JIRA ticket: {issue_key}")
            
        except JIRAError as e:
            logger.error(f"Failed to update JIRA ticket {issue_key}: {str(e)}")
            raise
    
    async def add_comment(self, issue_key: str, comment: str) -> None:
        """Add a comment to a JIRA ticket."""
        try:
            self.jira.add_comment(issue_key, comment)
            logger.info(f"Added comment to JIRA ticket: {issue_key}")
            
        except JIRAError as e:
            logger.error(f"Failed to add comment to JIRA ticket {issue_key}: {str(e)}")
            raise
    
    async def create_action_items(self, meeting_id: str, action_items: List[Dict]) -> List[str]:
        """Create JIRA tickets for action items from a meeting."""
        created_tickets = []
        
        for item in action_items:
            try:
                # Create description with meeting context
                description = f"""
                Action Item from Meeting: {meeting_id}
                
                Description: {item['description']}
                Assignee: {item['assignee']}
                Due Date: {item['due_date']}
                
                This ticket was automatically created by the Business Meeting Assistant Bot.
                """
                
                # Create the ticket
                issue_key = await self.create_ticket(
                    summary=item['description'][:100],  # JIRA has a limit on summary length
                    description=description,
                    issue_type="Task"
                )
                
                # Set assignee if provided
                if item.get('assignee'):
                    await self.update_ticket(issue_key, {'assignee': {'name': item['assignee']}})
                
                # Set due date if provided
                if item.get('due_date'):
                    await self.update_ticket(issue_key, {'duedate': item['due_date']})
                
                created_tickets.append(issue_key)
                
            except Exception as e:
                logger.error(f"Failed to create action item ticket: {str(e)}")
                continue
        
        return created_tickets
    
    async def link_tickets(self, source_key: str, target_keys: List[str], link_type: str = "relates to") -> None:
        """Create links between JIRA tickets."""
        try:
            for target_key in target_keys:
                self.jira.create_issue_link(
                    type=link_type,
                    inwardIssue=source_key,
                    outwardIssue=target_key
                )
            logger.info(f"Created links between {source_key} and {target_keys}")
            
        except JIRAError as e:
            logger.error(f"Failed to create ticket links: {str(e)}")
            raise
    
    async def get_ticket_status(self, issue_key: str) -> Dict:
        """Get the current status of a JIRA ticket."""
        try:
            issue = self.jira.issue(issue_key)
            return {
                'key': issue.key,
                'summary': issue.fields.summary,
                'status': issue.fields.status.name,
                'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
                'due_date': str(issue.fields.duedate) if issue.fields.duedate else None
            }
            
        except JIRAError as e:
            logger.error(f"Failed to get status for ticket {issue_key}: {str(e)}")
            raise 