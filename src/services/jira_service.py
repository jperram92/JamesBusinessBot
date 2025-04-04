import os
from typing import Dict, List, Optional
from jira import JIRA
import logging
from jira.exceptions import JIRAError

logger = logging.getLogger(__name__)

class JiraService:
    """JIRA service for ticket management."""
    
    def __init__(self, config: Dict):
        """Initialize the JIRA service with configuration."""
        self.config = config
        self.jira_config = config.get('jira', {})
        self.client = JIRA(
            server=self.jira_config.get('server'),
            basic_auth=(
                self.jira_config.get('username'),
                self.jira_config.get('api_token')
            )
        )
        self.project_key = self.jira_config.get('project_key')
        
        logger.info("JIRA service initialized")
    
    async def create_ticket(self, summary: str, description: str, assignee: Optional[str] = None, due_date: Optional[str] = None) -> str:
        """Create a new JIRA ticket."""
        try:
            # Prepare ticket fields
            fields = {
                'project': {'key': self.project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': 'Task'}
            }
            
            if assignee:
                fields['assignee'] = {'name': assignee}
            
            if due_date:
                fields['duedate'] = due_date
            
            # Create the ticket
            issue = self.client.create_issue(fields=fields)
            
            logger.info(f"Successfully created JIRA ticket: {issue.key}")
            return issue.key
        except Exception as e:
            logger.error(f"Failed to create JIRA ticket: {str(e)}")
            raise
    
    async def update_ticket(self, ticket_id: str, summary: Optional[str] = None, description: Optional[str] = None) -> bool:
        """Update an existing JIRA ticket."""
        try:
            # Get the issue
            issue = self.client.issue(ticket_id)
            
            # Prepare update fields
            fields = {}
            if summary:
                fields['summary'] = summary
            if description:
                fields['description'] = description
            
            # Update the ticket
            issue.update(fields=fields)
            
            logger.info(f"Successfully updated JIRA ticket: {ticket_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update JIRA ticket: {str(e)}")
            raise
    
    async def add_comment(self, ticket_id: str, comment: str) -> bool:
        """Add a comment to a JIRA ticket."""
        try:
            issue = self.client.issue(ticket_id)
            self.client.add_comment(issue, comment)
            
            logger.info(f"Successfully added comment to JIRA ticket: {ticket_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add comment to JIRA ticket: {str(e)}")
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
                    assignee=item.get('assignee'),
                    due_date=item.get('due_date')
                )
                
                created_tickets.append(issue_key)
                
            except Exception as e:
                logger.error(f"Failed to create action item ticket: {str(e)}")
                continue
        
        return created_tickets
    
    async def link_tickets(self, source_key: str, target_keys: List[str], link_type: str = "relates to") -> None:
        """Create links between JIRA tickets."""
        try:
            for target_key in target_keys:
                self.client.create_issue_link(
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
            issue = self.client.issue(issue_key)
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