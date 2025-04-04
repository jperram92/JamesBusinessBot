# Business Meeting Assistant Bot - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [API Reference](#api-reference)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

## Introduction

The Business Meeting Assistant Bot is a comprehensive solution for automating meeting management, note-taking, and follow-up tasks. It can join meetings on Microsoft Teams and Google Meet, transcribe conversations, generate summaries, update JIRA tickets, and create documentation.

### Key Features

- **Meeting Integration**: Automatically join Microsoft Teams and Google Meet meetings
- **Real-time Transcription**: Convert speech to text during meetings
- **AI-Powered Summaries**: Generate concise meeting summaries using OpenAI
- **Action Item Extraction**: Identify and track action items from meetings
- **JIRA Integration**: Update tickets with meeting information and create subtasks
- **Document Generation**: Create Word documents and PowerPoint presentations
- **RESTful API**: Integrate with your existing workflows

## Installation

### Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (for containerized deployment)
- Microsoft Teams and/or Google Meet account
- OpenAI API key
- JIRA account with API access

### Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/business-meeting-assistant.git
   cd business-meeting-assistant
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

### Docker Installation

1. Build and run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

2. Check the logs:
   ```bash
   docker-compose logs -f
   ```

## Configuration

### Environment Variables

Configure the following environment variables in your `.env` file:

```
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# JIRA Configuration
JIRA_API_TOKEN=your_jira_api_token_here
JIRA_EMAIL=your_jira_email_here
JIRA_URL=your_jira_url_here

# Microsoft Teams Configuration
TEAMS_APP_ID=your_teams_app_id_here
TEAMS_APP_PASSWORD=your_teams_app_password_here

# Google Meet Configuration
GOOGLE_MEET_CREDENTIALS=path_to_google_credentials.json

# Bot Configuration
BOT_EMAIL=your_bot_email@your-domain.com
BOT_NAME="Business Assistant Bot"

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
```

### Configuration File

Edit `src/config/config.yaml` to customize the bot's behavior:

```yaml
# Bot Configuration
bot:
  name: "Business Assistant Bot"
  email_domain: "your-domain.com"
  language: "en-US"

# Meeting Settings
meetings:
  teams:
    enabled: true
    auto_join: true
    record_audio: true
  google_meet:
    enabled: true
    auto_join: true
    record_audio: true

# OpenAI Settings
openai:
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 2000
  summary_prompt: |
    Please provide a comprehensive summary of the meeting, including:
    - Key decisions made
    - Action items
    - Next steps
    - Important discussion points

# JIRA Settings
jira:
  default_project: "PROJ"
  ticket_template: |
    Summary: {summary}
    Description: {description}
    Type: Task
    Priority: Medium
    Labels: meeting-notes

# Document Generation
documents:
  word:
    template_path: "templates/meeting_summary.docx"
    output_dir: "output/word"
  powerpoint:
    template_path: "templates/meeting_presentation.pptx"
    output_dir: "output/powerpoint"
```

## Usage

### Starting the Bot

```bash
# Start the API server
python src/main.py

# Or use the command-line tool
meeting-bot
```

### Inviting the Bot to Meetings

1. Add the bot's email address to your meeting invites
2. The bot will automatically join and start transcribing

### Using the API

#### Join a Meeting

```bash
curl -X POST "http://localhost:8000/join-meeting" \
  -H "Content-Type: application/json" \
  -d '{"meeting_id": "meeting-id", "platform": "teams"}'
```

#### Leave a Meeting

```bash
curl -X POST "http://localhost:8000/leave-meeting"
```

#### Generate Documents

```bash
curl -X POST "http://localhost:8000/generate-documents" \
  -H "Content-Type: application/json" \
  -d '{"meeting_id": "meeting-id", "content": "Meeting content", "format": "word"}'
```

#### Update JIRA

```bash
curl -X POST "http://localhost:8000/update-jira" \
  -H "Content-Type: application/json" \
  -d '{"meeting_id": "meeting-id", "jira_ticket_id": "PROJ-123"}'
```

### Document Templates

The bot uses templates from the `templates` directory to generate documents. You can customize these templates to match your organization's branding and requirements.

## API Reference

### Endpoints

#### POST /join-meeting

Join a meeting on the specified platform.

**Request Body:**
```json
{
  "meeting_id": "string",
  "platform": "string",
  "jira_ticket_id": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully joined meeting"
}
```

#### POST /leave-meeting

Leave the current meeting.

**Response:**
```json
{
  "status": "success",
  "message": "Successfully left meeting"
}
```

#### POST /generate-documents

Generate documents from meeting content.

**Request Body:**
```json
{
  "meeting_id": "string",
  "content": "string",
  "format": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "document_path": "string"
}
```

#### POST /update-jira

Update a JIRA ticket with meeting information.

**Request Body:**
```json
{
  "meeting_id": "string",
  "jira_ticket_id": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully updated JIRA ticket"
}
```

## Troubleshooting

### Common Issues

#### Bot Cannot Join Meetings

- Verify that the bot's email address is correctly configured
- Check that the meeting platform credentials are valid
- Ensure the bot has the necessary permissions

#### Transcription Issues

- Check that the OpenAI API key is valid
- Verify that the audio is being captured correctly
- Check the logs for specific error messages

#### JIRA Integration Problems

- Verify JIRA credentials and permissions
- Check that the JIRA project exists
- Ensure the ticket ID format is correct

### Logs

Logs are stored in the `logs` directory. Check `bot.log` for detailed information about the bot's operation.

## FAQ

### How do I set up the bot's email domain?

You need to configure an email domain for the bot to receive meeting invites. This typically involves setting up a Microsoft 365 or Google Workspace account for the bot.

### Can the bot join meetings on other platforms?

Currently, the bot supports Microsoft Teams and Google Meet. Support for other platforms may be added in future releases.

### How are meeting summaries generated?

Meeting summaries are generated using OpenAI's GPT models. The bot transcribes the meeting audio, processes the text, and uses a prompt to generate a structured summary.

### Can I customize the document templates?

Yes, you can customize the Word and PowerPoint templates in the `templates` directory to match your organization's branding and requirements.

### How do I update the bot?

```bash
# Pull the latest changes
git pull

# Rebuild the Docker container
docker-compose build
docker-compose up -d
``` 