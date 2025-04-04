# Business Meeting Assistant Bot - Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [Environment Setup](#environment-setup)
4. [Docker Deployment](#docker-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Backup and Recovery](#backup-and-recovery)
8. [Security Considerations](#security-considerations)

## Prerequisites

Before deploying the Business Meeting Assistant Bot, ensure you have:

1. **Required Accounts and API Keys**:
   - Microsoft Teams account with appropriate permissions
   - Google Workspace account with Google Meet access
   - OpenAI API key
   - JIRA account with API access

2. **Infrastructure Requirements**:
   - Docker and Docker Compose (for containerized deployment)
   - Kubernetes cluster (for Kubernetes deployment)
   - Sufficient storage for logs and generated documents
   - Network access to required services

3. **System Requirements**:
   - CPU: 2+ cores
   - RAM: 4GB minimum
   - Storage: 20GB minimum
   - Network: Stable internet connection

## Deployment Options

### 1. Docker Deployment
Best for:
- Small to medium deployments
- Single server setups
- Quick deployment and testing

### 2. Kubernetes Deployment
Best for:
- Large-scale deployments
- High availability requirements
- Multi-environment setups
- Automated scaling

## Environment Setup

1. Create a production environment file:
   ```bash
   cp .env.example .env.production
   ```

2. Configure the environment variables:
   ```env
   # API Keys
   OPENAI_API_KEY=your_openai_api_key
   JIRA_API_TOKEN=your_jira_api_token
   JIRA_EMAIL=your_jira_email
   JIRA_URL=your_jira_url

   # Bot Configuration
   BOT_NAME=Meeting Assistant
   BOT_EMAIL=assistant@yourdomain.com
   LOG_LEVEL=INFO

   # Meeting Settings
   TEAMS_ENABLED=true
   GOOGLE_MEET_ENABLED=true
   AUTO_JOIN_MEETINGS=true
   RECORD_AUDIO=true

   # Document Settings
   OUTPUT_DIR=/app/output
   TEMPLATE_DIR=/app/templates
   ```

3. Create required directories:
   ```bash
   mkdir -p logs output templates
   ```

## Docker Deployment

### 1. Build the Docker Image

```bash
# Build the image
docker build -t business-meeting-assistant:latest .

# Tag the image (if using a registry)
docker tag business-meeting-assistant:latest your-registry/business-meeting-assistant:latest
```

### 2. Configure Docker Compose

Create a `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  meeting-bot:
    image: business-meeting-assistant:latest
    container_name: meeting-bot
    restart: unless-stopped
    env_file:
      - .env.production
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
      - ./output:/app/output
      - ./templates:/app/templates
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 3. Deploy with Docker Compose

```bash
# Start the services
docker-compose -f docker-compose.prod.yml up -d

# Check the logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Kubernetes Deployment

### 1. Create Kubernetes Namespace

```bash
kubectl create namespace meeting-bot
kubectl config set-context --current --namespace=meeting-bot
```

### 2. Create Secrets

```bash
# Create secrets from .env file
kubectl create secret generic meeting-bot-secrets \
  --from-env-file=.env.production \
  --namespace=meeting-bot
```

### 3. Create ConfigMap for Templates

```bash
# Create ConfigMap from templates directory
kubectl create configmap meeting-bot-templates \
  --from-file=templates/ \
  --namespace=meeting-bot
```

### 4. Deploy the Application

1. Create deployment manifest (`kubernetes/deployment.yaml`):
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: meeting-bot
     namespace: meeting-bot
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
           image: your-registry/business-meeting-assistant:latest
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
           resources:
             requests:
               cpu: "500m"
               memory: "512Mi"
             limits:
               cpu: "1000m"
               memory: "1Gi"
           livenessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 30
             periodSeconds: 10
           readinessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 5
             periodSeconds: 5
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

2. Create service manifest (`kubernetes/service.yaml`):
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: meeting-bot
     namespace: meeting-bot
   spec:
     selector:
       app: meeting-bot
     ports:
     - port: 80
       targetPort: 8000
     type: ClusterIP
   ```

3. Apply the manifests:
   ```bash
   kubectl apply -f kubernetes/
   ```

### 5. Verify Deployment

```bash
# Check deployment status
kubectl get deployments -n meeting-bot

# Check pods
kubectl get pods -n meeting-bot

# Check logs
kubectl logs -f deployment/meeting-bot -n meeting-bot
```

## Monitoring and Logging

### 1. Configure Logging

The application uses Python's logging module with the following configuration:

```python
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/meeting_bot.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Set Up Monitoring

1. Add Prometheus metrics endpoint:
   ```python
   from prometheus_client import Counter, Histogram
   
   # Define metrics
   meeting_counter = Counter('meetings_processed_total', 'Total number of meetings processed')
   processing_time = Histogram('meeting_processing_seconds', 'Time spent processing meetings')
   ```

2. Configure Prometheus to scrape metrics:
   ```yaml
   # prometheus.yml
   scrape_configs:
     - job_name: 'meeting-bot'
       static_configs:
         - targets: ['meeting-bot:8000']
   ```

### 3. Set Up Alerts

Create alert rules in Prometheus:
```yaml
# alerts.yml
groups:
- name: meeting-bot
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: High error rate detected
```

## Backup and Recovery

### 1. Backup Strategy

1. **Configuration Backup**:
   ```bash
   # Backup configuration files
   tar -czf config_backup.tar.gz .env.production src/config/
   ```

2. **Data Backup**:
   ```bash
   # Backup logs and output
   tar -czf data_backup.tar.gz logs/ output/
   ```

3. **Automated Backup Script**:
   ```bash
   #!/bin/bash
   BACKUP_DIR="/backup/meeting-bot"
   DATE=$(date +%Y%m%d)
   
   # Create backup directory
   mkdir -p $BACKUP_DIR/$DATE
   
   # Backup configuration
   tar -czf $BACKUP_DIR/$DATE/config_backup.tar.gz .env.production src/config/
   
   # Backup data
   tar -czf $BACKUP_DIR/$DATE/data_backup.tar.gz logs/ output/
   
   # Clean old backups (keep last 7 days)
   find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} \;
   ```

### 2. Recovery Procedure

1. **Configuration Recovery**:
   ```bash
   # Restore configuration
   tar -xzf config_backup.tar.gz
   ```

2. **Data Recovery**:
   ```bash
   # Restore data
   tar -xzf data_backup.tar.gz
   ```

3. **Application Recovery**:
   ```bash
   # Restart the application
   docker-compose -f docker-compose.prod.yml restart
   # or
   kubectl rollout restart deployment/meeting-bot -n meeting-bot
   ```

## Security Considerations

### 1. API Security

1. **API Authentication**:
   ```python
   from fastapi import Security, HTTPException
   from fastapi.security.api_key import APIKeyHeader
   
   API_KEY_NAME = "X-API-Key"
   api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
   
   async def get_api_key(api_key_header: str = Security(api_key_header)):
       if api_key_header != os.getenv("API_KEY"):
           raise HTTPException(status_code=403, detail="Invalid API key")
       return api_key_header
   ```

2. **Rate Limiting**:
   ```python
   from fastapi import FastAPI
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   from slowapi.errors import RateLimitExceeded
   
   limiter = Limiter(key_func=get_remote_address)
   app = FastAPI()
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
   ```

### 2. Data Security

1. **Encryption at Rest**:
   - Use encrypted volumes for sensitive data
   - Implement file-level encryption for documents

2. **Secure Communication**:
   - Use TLS for all API endpoints
   - Implement mutual TLS for service-to-service communication

### 3. Access Control

1. **Role-Based Access Control**:
   ```python
   from enum import Enum
   from fastapi import Depends
   
   class Role(str, Enum):
       ADMIN = "admin"
       USER = "user"
   
   async def get_current_user(role: Role = Depends(get_role)):
       if role not in [Role.ADMIN, Role.USER]:
           raise HTTPException(status_code=403, detail="Invalid role")
       return role
   ```

2. **Audit Logging**:
   ```python
   import logging
   
   audit_logger = logging.getLogger('audit')
   audit_logger.setLevel(logging.INFO)
   
   def log_audit_event(user: str, action: str, resource: str):
       audit_logger.info(f"User: {user}, Action: {action}, Resource: {resource}")
   ``` 