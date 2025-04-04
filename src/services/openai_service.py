import os
import openai
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class OpenAIService:
    """OpenAI service for transcription and summarization."""
    
    def __init__(self, config: Dict):
        """Initialize the OpenAI service with configuration."""
        self.config = config
        openai.api_key = config['openai'].get('api_key')
        self.model = config['openai'].get('model', 'gpt-4')
        self.temperature = config['openai'].get('temperature', 0.7)
        self.max_tokens = config['openai'].get('max_tokens', 2000)
        self.summary_prompt = config['openai'].get('summary_prompt', '')
        
        logger.info("OpenAI service initialized")
        
        # Initialize OpenAI client
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
    async def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio data to text."""
        try:
            response = await openai.audio.transcriptions.create(
                file=audio_data,
                model="whisper-1",
                language="en"
            )
            return response.text
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {str(e)}")
            raise
            
    async def generate_summary(self, text: str) -> Dict[str, List[str]]:
        """Generate meeting summary and extract key information."""
        try:
            # Prepare the prompt
            prompt = f"{self.summary_prompt}\n\nMeeting Transcript:\n{text}"
            
            # Generate summary using OpenAI
            response = await openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes meetings and extracts key information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Parse the response
            summary_text = response.choices[0].message.content
            
            # Extract information (this is a simple implementation)
            lines = summary_text.split('\n')
            summary = []
            action_items = []
            key_points = []
            next_steps = []
            
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.lower().startswith('summary:'):
                    current_section = 'summary'
                elif line.lower().startswith('action items:'):
                    current_section = 'action_items'
                elif line.lower().startswith('key points:'):
                    current_section = 'key_points'
                elif line.lower().startswith('next steps:'):
                    current_section = 'next_steps'
                else:
                    if current_section == 'summary':
                        summary.append(line)
                    elif current_section == 'action_items':
                        action_items.append({'description': line})
                    elif current_section == 'key_points':
                        key_points.append(line)
                    elif current_section == 'next_steps':
                        next_steps.append(line)
            
            return {
                'summary': '\n'.join(summary),
                'action_items': action_items,
                'key_points': key_points,
                'next_steps': next_steps
            }
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
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
                model=self.model,
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
            logger.error(f"Error extracting action items: {str(e)}")
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
                model=self.model,
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
            logger.error(f"Error generating meeting insights: {str(e)}")
            raise 