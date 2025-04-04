import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ItineraryProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.logger = logging.getLogger(__name__)

    def process_itinerary(self, raw_itinerary: str) -> dict:
        """
        Process raw itinerary text using OpenAI to create a structured format.
        
        Args:
            raw_itinerary (str): The raw itinerary text from the user
            
        Returns:
            dict: A structured itinerary with sections and items
        """
        try:
            # Create the prompt for OpenAI
            prompt = f"""
            Please process the following meeting itinerary into a professional, structured format.
            Break it down into logical sections and items. Include any relevant details about timing,
            topics, and action items. Format the response as a JSON object with the following structure:
            {{
                "sections": [
                    {{
                        "title": "Meeting Details",
                        "items": ["Date: [date]", "Time: [time]", "Duration: [duration]", "Location/Platform: [location/platform]"]
                    }},
                    {{
                        "title": "Agenda",
                        "items": ["Item 1", "Item 2", ...]
                    }},
                    {{
                        "title": "Action Items",
                        "items": ["Action 1", "Action 2", ...]
                    }}
                ]
            }}

            Extract the date, time, and location from the text if available. If not explicitly mentioned,
            use reasonable defaults or mark as "To be determined". Make sure to include a clear agenda section
            with the main topics to be discussed.

            Raw Itinerary:
            {raw_itinerary}
            """

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a professional meeting organizer. Your task is to structure meeting itineraries in a clear, professional format. Always respond with valid JSON. Extract date, time, and location information when available."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            # Parse the response
            processed_text = response.choices[0].message.content.strip()
            
            # Remove any markdown code block indicators if present
            if processed_text.startswith('```json'):
                processed_text = processed_text[7:]
            if processed_text.endswith('```'):
                processed_text = processed_text[:-3]
            
            processed_text = processed_text.strip()
            
            try:
                # Try to parse the JSON response
                processed_itinerary = json.loads(processed_text)
                
                # Ensure we have the required sections
                required_sections = ["Meeting Details", "Agenda", "Action Items"]
                existing_sections = [section["title"] for section in processed_itinerary.get("sections", [])]
                
                # Add any missing sections
                for section_title in required_sections:
                    if section_title not in existing_sections:
                        processed_itinerary["sections"].append({
                            "title": section_title,
                            "items": ["To be determined"]
                        })
                
                return processed_itinerary
            except json.JSONDecodeError as e:
                # If JSON parsing fails, create a basic structure
                self.logger.warning(f"Failed to parse OpenAI response as JSON: {str(e)}. Creating basic structure.")
                return {
                    "sections": [
                        {
                            "title": "Meeting Details",
                            "items": ["Date: To be determined", "Time: To be determined", "Location: To be determined"]
                        },
                        {
                            "title": "Agenda",
                            "items": [processed_text]
                        },
                        {
                            "title": "Action Items",
                            "items": ["To be determined"]
                        }
                    ]
                }

        except Exception as e:
            self.logger.error(f"Error processing itinerary: {str(e)}")
            raise

    def format_for_email(self, processed_itinerary: dict) -> str:
        """
        Format the processed itinerary for email display in a concise, email-friendly format.
        
        Args:
            processed_itinerary (dict): The processed itinerary structure
            
        Returns:
            str: HTML formatted itinerary for email
        """
        try:
            # Extract key information
            sections = processed_itinerary.get('sections', [])
            
            # Find meeting details section if it exists
            meeting_details = None
            agenda_items = []
            action_items = []
            
            for section in sections:
                if section['title'].lower() in ['meeting details', 'meeting information', 'overview']:
                    meeting_details = section
                elif section['title'].lower() in ['agenda', 'topics', 'discussion points']:
                    agenda_items = section['items']
                elif section['title'].lower() in ['action items', 'next steps', 'follow-up']:
                    action_items = section['items']
            
            # Create a concise email format
            html = """
            <div style="font-family: Arial, sans-serif; color: #333;">
                <div style="margin-bottom: 20px;">
                    <h2 style="color: #333; margin-top: 0;">Meeting Summary</h2>
            """
            
            # Add meeting details if available
            if meeting_details:
                html += "<div style='margin-bottom: 15px;'>"
                for item in meeting_details['items']:
                    if any(keyword in item.lower() for keyword in ['date', 'time', 'duration', 'location', 'platform']):
                        html += f"<p style='margin: 5px 0;'><strong>{item.split(':')[0]}:</strong> {item.split(':')[1] if ':' in item else item}</p>"
                html += "</div>"
            
            # Add a brief overview paragraph
            html += """
                <p style="margin-bottom: 15px; line-height: 1.5;">
                    This meeting will focus on the key topics outlined below. Please review the agenda items and come prepared to discuss.
                </p>
            """
            
            # Add agenda items as bullet points
            if agenda_items:
                html += """
                <div style="margin-bottom: 15px;">
                    <h3 style="color: #333; margin-bottom: 10px;">Agenda</h3>
                    <ul style="list-style-type: disc; padding-left: 20px;">
                """
                
                for item in agenda_items[:5]:  # Limit to top 5 items for brevity
                    html += f"""
                    <li style="margin-bottom: 8px;">
                        {item}
                    </li>
                    """
                
                html += "</ul></div>"
            
            # Add action items if available
            if action_items:
                html += """
                <div style="margin-bottom: 15px;">
                    <h3 style="color: #333; margin-bottom: 10px;">Action Items</h3>
                    <ul style="list-style-type: disc; padding-left: 20px;">
                """
                
                for item in action_items[:3]:  # Limit to top 3 items for brevity
                    html += f"""
                    <li style="margin-bottom: 8px;">
                        {item}
                    </li>
                    """
                
                html += "</ul></div>"
            
            # Add a closing paragraph
            html += """
                <p style="margin-top: 15px; line-height: 1.5;">
                    Please confirm your attendance. If you have any questions or need to reschedule, please let me know as soon as possible.
                </p>
            """
            
            html += """
                </div>
            </div>
            """
            
            return html
            
        except Exception as e:
            self.logger.error(f"Error formatting itinerary for email: {str(e)}")
            raise 