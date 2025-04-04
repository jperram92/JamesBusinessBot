# Business Meeting Assistant Bot - Admin Guide

## Table of Contents
1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)
8. [Security Considerations](#security-considerations)
9. [Backup and Recovery](#backup-and-recovery)
10. [Updating the Bot](#updating-the-bot)

## Introduction

The Business Meeting Assistant Bot is a comprehensive solution for automating meeting management, transcription, documentation, and task tracking. This admin guide provides detailed instructions for setting up, configuring, and maintaining the bot in your organization.

## System Requirements

### Hardware Requirements
- CPU: 2+ cores
- RAM: 4GB minimum, 8GB recommended
- Storage: 20GB minimum for application and logs
- Network: Stable internet connection with low latency

### Software Requirements
- Operating System: Linux (Ubuntu 20.04+ recommended), macOS, or Windows 10+
- Docker: 20.10+ (for containerized deployment)
- Kubernetes: 1.20+ (for Kubernetes deployment)
- Python: 3.9+ (for local deployment)

### External Service Requirements
- Microsoft Teams account with appropriate permissions
- Google Workspace account with Google Meet access
- OpenAI API key
- JIRA account with API access
- SMTP server for email notifications (optional)

## Installation

### Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/meeting-assistant-bot.git
   cd meeting-assistant-bot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create necessary directories:
   ```bash
   mkdir -p logs data
   ```

### Docker Installation

1. Build the Docker image:
   ```bash
   docker build -t meeting-assistant-bot:latest .
   ```

2. Run the container:
   ```bash
   docker run -d \
     --name meeting-bot \
     -p 8000:8000 \
     -v $(pwd)/logs:/app/logs \
     -v $(pwd)/data:/app/data \
     --env-file .env \
     meeting-assistant-bot:latest
   ```

### Docker Compose Installation

1. Create a `.env` file with your configuration (see Configuration section)

2. Start the services:
   ```bash
   docker-compose up -d
   ```

### Kubernetes Installation

1. Create a namespace:
   ```bash
   kubectl create namespace meeting-bot
   ```

2. Apply the Kubernetes manifests:
   ```bash
   kubectl apply -f k8s/secrets.yaml
   kubectl apply -f k8s/persistent-volume-claims.yaml
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   kubectl apply -f k8s/ingress.yaml
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# JIRA Configuration
JIRA_SERVER=https://your-jira-instance.atlassian.net
JIRA_USERNAME=your-jira-username
JIRA_API_TOKEN=your-jira-api-token
JIRA_PROJECT_KEY=your-jira-project-key

# Microsoft Teams Configuration
TEAMS_APP_ID=your-teams-app-id
TEAMS_APP_PASSWORD=your-teams-app-password

# Google Meet Configuration
GOOGLE_CREDENTIALS_PATH=/app/secrets/google-credentials.json

# Grafana Configuration
GRAFANA_ADMIN_PASSWORD=your-grafana-admin-password
```

### Configuration File

Edit `src/config/config.yaml` to customize the bot's behavior:

```yaml
meetings:
  teams:
    enabled: true
    app_id: ${TEAMS_APP_ID}
    app_password: ${TEAMS_APP_PASSWORD}
  google_meet:
    enabled: true
    credentials_path: ${GOOGLE_CREDENTIALS_PATH}
    scopes:
      - https://www.googleapis.com/auth/calendar
      - https://www.googleapis.com/auth/calendar.events
      - https://www.googleapis.com/auth/meetings.space.created

openai:
  api_key: ${OPENAI_API_KEY}
  model: gpt-4
  max_tokens: 2000
  temperature: 0.7

jira:
  server: ${JIRA_SERVER}
  username: ${JIRA_USERNAME}
  api_token: ${JIRA_API_TOKEN}
  project_key: ${JIRA_PROJECT_KEY}

documents:
  template_dir: templates
  output_dir: data/documents

logging:
  level: INFO
  file: logs/meeting-bot.log
  max_size: 10MB
  backup_count: 5
```

## Usage

### Starting the Bot

#### Local Deployment
```bash
python -m src.main
```

#### Docker Deployment
```bash
docker start meeting-bot
```

#### Kubernetes Deployment
```bash
kubectl rollout restart deployment/meeting-bot -n meeting-bot
```

### Joining Meetings

The bot can join meetings through the API:

```bash
curl -X POST "http://localhost:8000/meetings/join" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "meeting-id-123",
    "platform": "teams",
    "title": "Weekly Standup",
    "description": "Weekly team standup meeting"
  }'
```

### Generating Documents

Generate meeting documents:

```bash
curl -X POST "http://localhost:8000/documents/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "meeting-id-123",
    "document_type": "summary",
    "format": "docx"
  }'
```

### Updating JIRA

Create action items in JIRA:

```bash
curl -X POST "http://localhost:8000/jira/update" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "meeting-id-123",
    "action_items": [
      {
        "description": "Complete the project proposal",
        "assignee": "john.doe@example.com",
        "due_date": "2023-12-31"
      }
    ],
    "summary": "Weekly Standup Summary",
    "description": "Key points discussed in the weekly standup meeting"
  }'
```

### Checking Meeting Status

```bash
curl "http://localhost:8000/meetings/meeting-id-123/status"
```

## Monitoring and Maintenance

### Accessing Monitoring Dashboards

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (default credentials: admin/admin)

### Setting Up Alerts

1. Configure alert notifications in Prometheus:
   ```bash
   kubectl apply -f monitoring/prometheus-rules.yaml
   ```

2. Set up alert channels in Grafana:
   - Log in to Grafana
   - Go to Alerting > Notification channels
   - Add your preferred notification channel (email, Slack, etc.)

### Log Management

Logs are stored in the `logs` directory. Rotate logs regularly:

```bash
# For local deployment
logrotate -f logrotate.conf

# For Docker deployment
docker exec meeting-bot logrotate -f /app/logrotate.conf
```

### Health Checks

Monitor the bot's health:

```bash
curl "http://localhost:8000/health"
```

## Troubleshooting

### Common Issues

#### Bot Cannot Join Meetings

1. Check credentials:
   ```bash
   # For Teams
   curl -X POST "http://localhost:8000/meetings/join" \
     -H "Content-Type: application/json" \
     -d '{"meeting_id": "test-meeting", "platform": "teams"}'
   
   # Check logs
   tail -f logs/meeting-bot.log
   ```

2. Verify network connectivity:
   ```bash
   # Test Teams connectivity
   curl -v https://teams.microsoft.com
   
   # Test Google Meet connectivity
   curl -v https://meet.google.com
   ```

#### Transcription Issues

1. Check OpenAI API key:
   ```bash
   curl -X POST "https://api.openai.com/v1/chat/completions" \
     -H "Authorization: Bearer $OPENAI_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model": "gpt-4", "messages": [{"role": "user", "content": "Hello"}]}'
   ```

2. Verify audio capture:
   ```bash
   # Check if audio is being captured
   docker exec meeting-bot ls -la /app/data/audio
   ```

#### JIRA Integration Problems

1. Test JIRA connection:
   ```bash
   curl -u $JIRA_USERNAME:$JIRA_API_TOKEN https://$JIRA_SERVER/rest/api/2/myself
   ```

2. Check JIRA project access:
   ```bash
   curl -u $JIRA_USERNAME:$JIRA_API_TOKEN https://$JIRA_SERVER/rest/api/2/project/$JIRA_PROJECT_KEY
   ```

### Log Analysis

Analyze logs for errors:

```bash
grep -i error logs/meeting-bot.log
grep -i exception logs/meeting-bot.log
```

## Security Considerations

### API Security

1. Enable authentication for the API:
   ```bash
   # Add to docker-compose.yml
   environment:
     - API_KEY=your-secure-api-key
   ```

2. Use the API key in requests:
   ```bash
   curl -H "X-API-Key: your-secure-api-key" http://localhost:8000/health
   ```

### Data Security

1. Encrypt sensitive data:
   ```bash
   # For Kubernetes
   kubectl create secret generic meeting-bot-encryption-key --from-literal=key=$(openssl rand -base64 32)
   ```

2. Secure storage:
   ```bash
   # Set proper permissions
   chmod 600 .env
   chmod 700 data
   ```

### Access Control

1. Implement role-based access:
   ```bash
   # Add to docker-compose.yml
   environment:
     - ADMIN_USERS=admin1@example.com,admin2@example.com
   ```

2. Audit logging:
   ```bash
   # Enable audit logging
   echo "audit_log: true" >> src/config/config.yaml
   ```

## Backup and Recovery

### Configuration Backup

```bash
# Backup configuration
tar -czf config-backup-$(date +%Y%m%d).tar.gz src/config/ .env

# Restore configuration
tar -xzf config-backup-20230101.tar.gz
```

### Data Backup

```bash
# Backup data
tar -czf data-backup-$(date +%Y%m%d).tar.gz data/

# Restore data
tar -xzf data-backup-20230101.tar.gz
```

### Automated Backup Script

Create a backup script (`backup.sh`):

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup configuration
tar -czf $BACKUP_DIR/config-$DATE.tar.gz src/config/ .env

# Backup data
tar -czf $BACKUP_DIR/data-$DATE.tar.gz data/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

Add to crontab:
```
0 2 * * * /path/to/backup.sh
```

## Updating the Bot

### Local Update

```bash
# Pull latest changes
git pull

# Update dependencies
pip install -r requirements.txt

# Restart the bot
pkill -f "python -m src.main"
python -m src.main
```

### Docker Update

```bash
# Pull latest image
docker pull meeting-assistant-bot:latest

# Stop and remove old container
docker stop meeting-bot
docker rm meeting-bot

# Start new container
docker run -d \
  --name meeting-bot \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  meeting-assistant-bot:latest
```

### Kubernetes Update

```bash
# Update deployment
kubectl set image deployment/meeting-bot meeting-bot=meeting-assistant-bot:latest -n meeting-bot

# Monitor rollout
kubectl rollout status deployment/meeting-bot -n meeting-bot
```

---

For additional support, please contact the development team or refer to the developer documentation. 