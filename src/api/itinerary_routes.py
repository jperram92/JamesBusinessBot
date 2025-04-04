from flask import Blueprint, request, jsonify
from src.utils.itinerary_processor import ItineraryProcessor
from src.services.email_service import EmailService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
itinerary_bp = Blueprint('itinerary', __name__)

# Initialize processor and email service
processor = ItineraryProcessor()
email_service = EmailService()

@itinerary_bp.route('/api/process-itinerary', methods=['POST'])
def process_itinerary():
    """Process a raw itinerary and return a structured format."""
    try:
        data = request.get_json()
        raw_itinerary = data.get('rawItinerary')
        
        if not raw_itinerary:
            return jsonify({'error': 'No itinerary provided'}), 400
            
        # Process the itinerary
        processed_itinerary = processor.process_itinerary(raw_itinerary)
        
        return jsonify(processed_itinerary)
        
    except Exception as e:
        logger.error(f"Error processing itinerary: {str(e)}")
        return jsonify({'error': 'Failed to process itinerary'}), 500

@itinerary_bp.route('/api/send-itinerary', methods=['POST'])
def send_itinerary():
    """Process and send an itinerary via email."""
    try:
        data = request.get_json()
        raw_itinerary = data.get('rawItinerary')
        recipient_email = data.get('recipientEmail')
        subject = data.get('subject', 'Meeting Invitation')
        additional_recipients = data.get('additionalRecipients', [])
        
        if not raw_itinerary:
            return jsonify({'error': 'No itinerary provided'}), 400
            
        if not recipient_email:
            return jsonify({'error': 'No recipient email provided'}), 400
            
        # Process the itinerary
        processed_itinerary = processor.process_itinerary(raw_itinerary)
        
        # Format the itinerary for email
        formatted_itinerary = processor.format_for_email(processed_itinerary)
        
        # Send the email
        success = email_service.send_meeting_invitation(
            recipient_email=recipient_email,
            subject=subject,
            formatted_itinerary=formatted_itinerary,
            additional_recipients=additional_recipients,
            meeting_details=request.json.get('meetingDetails', {})
        )
        
        if success:
            return jsonify({
                'message': 'Itinerary sent successfully',
                'processed_itinerary': processed_itinerary
            })
        else:
            return jsonify({'error': 'Failed to send email'}), 500
        
    except Exception as e:
        logger.error(f"Error sending itinerary: {str(e)}")
        return jsonify({'error': 'Failed to send itinerary'}), 500

@itinerary_bp.route('/api/format-itinerary', methods=['POST'])
def format_itinerary():
    """Format a processed itinerary for email display."""
    try:
        data = request.get_json()
        processed_itinerary = data.get('processedItinerary')
        
        if not processed_itinerary:
            return jsonify({'error': 'No processed itinerary provided'}), 400
            
        # Format the itinerary for email
        formatted_html = processor.format_for_email(processed_itinerary)
        
        return jsonify({'html': formatted_html})
        
    except Exception as e:
        logger.error(f"Error formatting itinerary: {str(e)}")
        return jsonify({'error': 'Failed to format itinerary'}), 500 