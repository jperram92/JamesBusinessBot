# Business Meeting Assistant Bot - Developer Guide

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Code Structure](#code-structure)
4. [Adding New Features](#adding-new-features)
5. [Testing](#testing)
6. [Deployment](#deployment)
7. [Contributing](#contributing)

## Architecture Overview

The Business Meeting Assistant Bot is built with a modular architecture that separates concerns into distinct components:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Meeting Bot    │────▶│  API Server     │────▶│  External APIs  │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Meeting        │     │  Document       │     │  OpenAI         │
│  Services       │     │  Generation     │     │  Integration    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Teams/Google   │     │  Word/PowerPoint│     │  JIRA           │
│  Meet Integration│     │  Generation     │     │  Integration    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Key Components

1. **Meeting Bot**: Core bot functionality that orchestrates the various services
2. **API Server**: FastAPI-based REST API for external integration
3. **Meeting Services**: Handles joining and interacting with meetings
4. **Document Generation**: Creates Word and PowerPoint documents
5. **OpenAI Integration**: Handles transcription and summarization
6. **JIRA Integration**: Updates tickets with meeting information

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Docker and Docker Compose (for containerized development)
- VS Code or your preferred IDE

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/business-meeting-assistant.git
   cd business-meeting-assistant
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

5. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your development credentials
   ```

### Running the Application in Development Mode

```bash
# Start the API server with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Code Structure

```
business-meeting-assistant/
├── src/
│   ├── bot/
│   │   └── meeting_bot.py       # Core bot functionality
│   ├── services/
│   │   ├── teams_service.py     # Microsoft Teams integration
│   │   ├── google_meet_service.py # Google Meet integration
│   │   ├── openai_service.py    # OpenAI integration
│   │   ├── jira_service.py      # JIRA integration
│   │   └── document_service.py  # Document generation
│   ├── utils/
│   │   └── config_loader.py     # Configuration management
│   ├── config/
│   │   └── config.yaml          # Configuration file
│   ├── templates/
│   │   ├── meeting_summary.docx # Word template
│   │   └── meeting_presentation.pptx # PowerPoint template
│   └── main.py                  # API server entry point
├── tests/
│   ├── test_meeting_bot.py      # Bot tests
│   └── test_api.py              # API tests
├── docs/
│   ├── user_guide.md            # User documentation
│   └── developer_guide.md       # Developer documentation
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose configuration
├── requirements.txt             # Dependencies
├── setup.py                     # Package configuration
├── pytest.ini                   # Test configuration
└── README.md                    # Project overview
```

## Adding New Features

### Adding a New Meeting Platform

1. Create a new service class in `src/services/`:
   ```python
   # src/services/zoom_service.py
   
   class ZoomService:
       def __init__(self, config):
           # Initialize Zoom client
           
       async def join_meeting(self, meeting_id):
           # Join a Zoom meeting
           
       async def leave_meeting(self):
           # Leave the current meeting
           
       async def capture_audio(self):
           # Capture audio from the meeting
   ```

2. Update the `MeetingBot` class to use the new service:
   ```python
   # src/bot/meeting_bot.py
   
   from ..services.zoom_service import ZoomService
   
   class MeetingBot:
       def __init__(self, config_path: str = "src/config/config.yaml"):
           # ...
           self.zoom_service = ZoomService(self.config) if self.config['meetings']['zoom']['enabled'] else None
           # ...
           
       async def join_meeting(self, meeting_id: str, platform: str = "teams"):
           # ...
           elif platform.lower() == "zoom" and self.zoom_service:
               self.current_meeting = await self.zoom_service.join_meeting(meeting_id)
           # ...
   ```

3. Update the configuration file:
   ```yaml
   # src/config/config.yaml
   
   meetings:
     # ...
     zoom:
       enabled: true
       auto_join: true
       record_audio: true
   ```

4. Add tests for the new functionality:
   ```python
   # tests/test_meeting_bot.py
   
   @pytest.mark.asyncio
   async def test_join_meeting_zoom(meeting_bot):
       """Test joining a Zoom meeting."""
       result = await meeting_bot.join_meeting("test-meeting-id", "zoom")
       assert result is True
       assert meeting_bot.current_meeting is not None
   ```

### Adding a New Document Type

1. Update the `DocumentService` class:
   ```python
   # src/services/document_service.py
   
   async def create_pdf(self, meeting_id: str, content: str) -> str:
       """Create a PDF document from meeting content."""
       # Implementation
   ```

2. Update the API endpoint:
   ```python
   # src/main.py
   
   @app.post("/generate-documents")
   async def generate_documents(request: DocumentRequest):
       # ...
       elif request.format == "pdf":
           doc_path = await bot.document_service.create_pdf(
               request.meeting_id,
               request.content
           )
           return {"status": "success", "document_path": doc_path}
       # ...
   ```

3. Add tests for the new functionality:
   ```python
   # tests/test_api.py
   
   def test_generate_documents_pdf(mock_meeting_bot):
       """Test generating a PDF document via API."""
       # Test implementation
   ```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src

# Run specific test file
pytest tests/test_meeting_bot.py

# Run tests matching a pattern
pytest -k "join_meeting"
```

### Writing Tests

- Use pytest fixtures for setup and teardown
- Mock external dependencies
- Test both success and failure cases
- Use descriptive test names

Example:
```python
@pytest.mark.asyncio
async def test_process_audio_with_empty_buffer(meeting_bot):
    """Test processing audio when buffer is empty."""
    await meeting_bot.process_audio(b"test audio data")
    assert len(meeting_bot.transcription_buffer) == 1
```

## Deployment

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t business-meeting-assistant .
   ```

2. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

### Kubernetes Deployment

1. Create Kubernetes manifests:
   ```yaml
   # kubernetes/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: meeting-bot
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: meeting-bot
     template:
       metadata:
         labels:
           app: meeting-bot
       spec:
         containers:
         - name: meeting-bot
           image: business-meeting-assistant:latest
           ports:
           - containerPort: 8000
           envFrom:
           - secretRef:
               name: meeting-bot-secrets
           volumeMounts:
           - name: logs
             mountPath: /app/logs
           - name: output
             mountPath: /app/output
           - name: templates
             mountPath: /app/templates
         volumes:
         - name: logs
           persistentVolumeClaim:
             claimName: meeting-bot-logs
         - name: output
           persistentVolumeClaim:
             claimName: meeting-bot-output
         - name: templates
           configMap:
             name: meeting-bot-templates
   ```

2. Apply the manifests:
   ```bash
   kubectl apply -f kubernetes/
   ```

## Contributing

### Contributing Guidelines

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `pytest`
5. Commit your changes: `git commit -m 'Add my feature'`
6. Push to the branch: `git push origin feature/my-feature`
7. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions and classes
- Keep functions small and focused

### Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the documentation if needed
3. The PR will be merged once you have the sign-off of at least one maintainer 