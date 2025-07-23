# Deployment Instructions

## Development
```bash
# Using Docker Compose
docker-compose -f docker/docker-compose.dev.yml up -d

# Local development
pip install -r requirements.txt
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8002
```

## Production
```bash
# Build and deploy
docker-compose -f docker/docker-compose.yml up -d

# Environment variables
cp .env.example .env
# Edit .env with production values
```

## Database Migration
```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```
