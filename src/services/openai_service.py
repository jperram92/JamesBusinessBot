import os
import openai
from typing import Optional, Dict, List
import logging

class OpenAIService:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger('OpenAIService')
        
        # Initialize OpenAI client
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
    async def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio data using OpenAI's Whisper model."""
        try:
            response = await openai.Audio.atranscribe(
                model="whisper-1",
                file=audio_data
            )
            return response.text
        except Exception as e:
            self.logger.error(f"Error transcribing audio: {str(e)}")
            raise
            
    async def generate_summary(self, text: str) -> str:
        """Generate a summary of the meeting using OpenAI."""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.config['openai']['model'],
                messages=[
                    {"role": "system", "content": self.config['openai']['summary_prompt']},
                    {"role": "user", "content": text}
                ],
                temperature=self.config['openai']['temperature'],
                max_tokens=self.config['openai']['max_tokens']
            )
            return response.choices[0].message.content
        except Exception as e:
            this.logger.error(f"Error generating summary: {str(e)}")
            raise
            
    async def extract_action_items(self, text: str) -> List[Dict]:
        """Extract action items from the meeting transcript."""
        try:
            prompt = """
            Please extract action items from the following meeting transcript.
            For each action item, provide:
            - Description
            - Assignee (if mentioned)
            - Due date (if mentioned)
            - Priority (High/Medium/Low)
            Format the response as a JSON array of objects.
            """
            
            response = await openai.ChatCompletion.acreate(
                model=this.config['openai']['model'],
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3
            )
            
            # Parse the response into a list of action items
            action_items = eval(response.choices[0].message.content)
            return action_items
        except Exception as e:
            this.logger.error(f"Error extracting action items: {str(e)}")
            raise
            
    async def generate_meeting_insights(self, text: str) -> Dict:
        """Generate insights from the meeting transcript."""
        try:
            prompt = """
            Please analyze the following meeting transcript and provide:
            1. Key decisions made
            2. Main topics discussed
            3. Sentiment analysis
            4. Risk factors identified
            5. Next steps
            Format the response as a JSON object.
            """
            
            response = await openai.ChatCompletion.acreate(
                model=this.config['openai']['model'],
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.5
            )
            
            # Parse the response into a dictionary of insights
            insights = eval(response.choices[0].message.content)
            return insights
        except Exception as e:
            this.logger.error(f"Error generating meeting insights: {str(e)}")
            raise 