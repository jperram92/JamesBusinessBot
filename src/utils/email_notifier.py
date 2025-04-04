import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from datetime import datetime
from zoneinfo import ZoneInfo
from .itinerary_processor import ItineraryProcessor

class EmailNotifier:
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL')
        if not self.api_key or not self.from_email:
            raise ValueError("SENDGRID_API_KEY and FROM_EMAIL must be set in environment variables")
        
        self.client = SendGridAPIClient(self.api_key)
        self.logger = logging.getLogger(__name__)
        self.itinerary_processor = ItineraryProcessor()

    def _format_datetime(self, dt_str):
        """Convert UTC datetime string to a more readable format."""
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            # Convert to Australia/Sydney timezone
            dt_sydney = dt.astimezone(ZoneInfo('Australia/Sydney'))
            return dt_sydney.strftime('%A, %d %B %Y at %I:%M %p AEST')
        except Exception as e:
            self.logger.error(f"Error formatting datetime: {str(e)}")
            return dt_str

    def send_meeting_invitation(self, to_email: str, meeting_details: dict) -> bool:
        """
        Send a meeting invitation email using SendGrid.
        
        Args:
            to_email (str): Recipient's email address
            meeting_details (dict): Dictionary containing meeting information
                {
                    'title': str,
                    'start_time': str,
                    'end_time': str,
                    'description': str,
                    'meet_link': str
                }
        
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Format dates
            start_time = self._format_datetime(meeting_details['start_time'])
            
            # Handle end time - either format it if it's a datetime string or use it directly if it's already formatted
            if 'end_time' in meeting_details and meeting_details['end_time']:
                try:
                    # Try to format it as a datetime string
                    end_time = self._format_datetime(meeting_details['end_time'])
                except:
                    # If that fails, use it directly (it might already be formatted)
                    end_time = meeting_details['end_time']
            else:
                end_time = "To be determined"
            
            # Create email content with improved styling
            subject = f"Meeting Invitation: {meeting_details['title']}"
            
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #ffffff; padding: 20px; border-bottom: 1px solid #e9ecef; }}
                    .content {{ background-color: #ffffff; padding: 20px; }}
                    .meeting-details {{ margin-bottom: 20px; }}
                    .meeting-time {{ background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin: 15px 0; }}
                    .description {{ background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin: 15px 0; }}
                    .button {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: #ffffff; text-decoration: none; border-radius: 4px; margin: 15px 0; }}
                    .footer {{ margin-top: 20px; padding: 20px; text-align: center; font-size: 12px; color: #6c757d; border-top: 1px solid #dee2e6; }}
                    .business-info {{ margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 4px; }}
                    .contact-info {{ margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 4px; }}
                    h1, h2, h3 {{ color: #333; }}
                    a {{ color: #007bff; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="margin: 0; font-size: 24px;">Meeting Invitation</h1>
                    </div>
                    
                    <div class="content">
                        <div class="meeting-details">
                            <h2 style="margin-top: 0;">{meeting_details.get('title', 'Meeting')}</h2>
                            
                            <div class="meeting-time">
                                <h3 style="margin-top: 0;">Date and Time</h3>
                                <p style="margin: 0;">
                                    <strong>Date:</strong> {meeting_details.get('date', 'To be determined')}<br>
                                    <strong>Start Time:</strong> {start_time}<br>
                                    <strong>End Time:</strong> {end_time}<br>
                                    <strong>Duration:</strong> {meeting_details.get('duration', 'To be determined')}
                                </p>
                            </div>
                            
                            <div class="description">
                                <h3 style="margin-top: 0;">Description</h3>
                                <p style="margin: 0;">{meeting_details['description']}</p>
                            </div>
                            """
            
            # Add itinerary if available
            if meeting_details.get('itinerary'):
                body += f"""
                            <div style="margin-top: 20px;">
                                {meeting_details['itinerary']}
                            </div>
                            """
            
            if meeting_details.get('meet_link') and meeting_details['meet_link'] != 'No meet link generated':
                body += f"""
                            <div style="text-align: center; margin-top: 20px;">
                                <a href="{meeting_details['meet_link']}" class="button">Join Meeting</a>
                            </div>
                            """
            
            body += """
                        </div>
                        
                        <div class="business-info">
                            <h3 style="margin-top: 0;">Business Information</h3>
                            <p style="margin: 0;">
                                <strong>Website:</strong> <a href="https://www.jamesperram.com.au">www.jamesperram.com.au</a><br>
                                <strong>Business Hours:</strong> Monday - Friday, 9:00 AM - 5:00 PM AEST
                            </p>
                        </div>
                        
                        <div class="contact-info">
                            <h3 style="margin-top: 0;">Need Assistance?</h3>
                            <p style="margin: 0;">
                                If you have any questions or need to reschedule this meeting, please contact:<br>
                                <strong>James Perram</strong><br>
                                Email: <a href="mailto:contact@jamesperram.com.au">contact@jamesperram.com.au</a><br>
                                Phone: +61 XXX XXX XXX
                            </p>
                        </div>
                        
                        <div class="footer">
                            <p>This invitation was sent by James Perram's Business Meeting Assistant</p>
                            <p style="margin-top: 10px;">
                                © 2024 James Perram. All rights reserved.<br>
                                <a href="https://www.jamesperram.com.au/privacy">Privacy Policy</a> | 
                                <a href="https://www.jamesperram.com.au/terms">Terms of Service</a>
                            </p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create the email message
            message = Mail(
                from_email=(self.from_email, "James Perram"),
                to_emails=to_email,
                subject=subject,
                html_content=body
            )
            
            # Send the email
            response = self.client.send(message)
            
            if response.status_code == 202:
                self.logger.info(f"Meeting invitation sent successfully to {to_email}")
                return True
            else:
                self.logger.error(f"Failed to send email. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False 