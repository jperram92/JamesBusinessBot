# Business Meeting Assistant Bot

A comprehensive meeting assistant bot that can join meetings, take notes, update JIRA tickets, and generate documentation.

## Features

- Join Microsoft Teams and Google Meet meetings
- Real-time meeting transcription
- AI-powered meeting summarization using OpenAI
- Automatic JIRA ticket updates
- Generate Word and PowerPoint documents from meeting notes
- Customizable prompts and responses

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your credentials:
   ```
   OPENAI_API_KEY=your_openai_key
   JIRA_API_TOKEN=your_jira_token
   JIRA_EMAIL=your_email
   JIRA_URL=your_jira_url
   TEAMS_APP_ID=your_teams_app_id
   TEAMS_APP_PASSWORD=your_teams_app_password
   GOOGLE_MEET_CREDENTIALS=path_to_credentials.json
   ```

4. Run the bot:
   ```bash
   python src/main.py
   ```

## Configuration

The bot can be configured through the `config.yaml` file:
- Meeting settings
- JIRA project mappings
- Document templates
- AI response settings

## Usage

1. Invite the bot to your meetings using the configured email
2. The bot will automatically join and start transcribing
3. Use commands in the meeting chat to:
   - Generate summaries
   - Update JIRA tickets
   - Create documents
   - Get meeting insights

## License

MIT License

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests. 