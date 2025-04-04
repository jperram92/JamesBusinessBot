import os
from typing import List, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailService:
    def __init__(self):
        self.sendgrid_client = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        self.from_email = os.getenv('FROM_EMAIL')
        self.default_recipient = os.getenv('RECIPIENT_EMAIL')

    def send_meeting_invitation(
        self,
        recipient_email: str,
        subject: str,
        formatted_itinerary: str,
        additional_recipients: Optional[List[str]] = None,
        meeting_details: Optional[dict] = None
    ) -> bool:
        """
        Send a meeting invitation email with the formatted itinerary.
        
        Args:
            recipient_email (str): Primary recipient email address
            subject (str): Email subject line
            formatted_itinerary (str): HTML formatted itinerary
            additional_recipients (List[str], optional): List of additional recipient emails
            meeting_details (dict, optional): Dictionary containing meeting details
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Create email content
            email_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{subject}</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2c3e50; margin-bottom: 20px;">{subject}</h1>
                    
                    {formatted_itinerary}
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; font-size: 12px; color: #6c757d;">
                        <p>This is an automated meeting invitation. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Create the email
            message = Mail(
                from_email=Email(self.from_email, "Meeting Assistant"),
                to_emails=[To(recipient_email)] + ([To(email) for email in additional_recipients] if additional_recipients else []),
                subject=subject,
                html_content=HtmlContent(email_content)
            )

            # Send the email
            response = self.sendgrid_client.send(message)
            
            # Check if the email was sent successfully
            if response.status_code in [200, 201, 202]:
                return True
            else:
                print(f"Failed to send email. Status code: {response.status_code}")
                return False

        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

    def send_meeting_update(
        self,
        recipient_email: str,
        subject: str,
        formatted_itinerary: str,
        update_message: str,
        additional_recipients: Optional[List[str]] = None
    ) -> bool:
        """
        Send a meeting update email with the formatted itinerary.
        
        Args:
            recipient_email (str): Primary recipient email address
            subject (str): Email subject line
            formatted_itinerary (str): HTML formatted itinerary
            update_message (str): Message explaining the update
            additional_recipients (List[str], optional): List of additional recipient emails
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Create email content
            email_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{subject}</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2c3e50; margin-bottom: 20px;">{subject}</h1>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                        <p style="margin: 0;">{update_message}</p>
                    </div>
                    
                    {formatted_itinerary}
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; font-size: 12px; color: #6c757d;">
                        <p>This is an automated meeting update. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Create the email
            message = Mail(
                from_email=Email(self.from_email, "Meeting Assistant"),
                to_emails=[To(recipient_email)] + ([To(email) for email in additional_recipients] if additional_recipients else []),
                subject=subject,
                html_content=HtmlContent(email_content)
            )

            # Send the email
            response = self.sendgrid_client.send(message)
            
            # Check if the email was sent successfully
            if response.status_code in [200, 201, 202]:
                return True
            else:
                print(f"Failed to send email. Status code: {response.status_code}")
                return False

        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False 