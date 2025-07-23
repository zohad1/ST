# Payment Service

## Overview
Payment service for TikTok Shop Creator CRM platform handling creator earnings, payouts, and financial operations.

## Features
- Creator earnings calculation
- Automated payment processing
- Stripe and Fanbasis integration
- Referral bonus system
- Payment scheduling and automation
- Webhook handling for payment status updates

## Quick Start
1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Run `docker-compose -f docker/docker-compose.dev.yml up -d`
4. Access API at `http://localhost:8002`

## API Documentation
- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`

## Development

### Installation
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running locally
```bash
uvicorn app.main:app --reload --port 8002
```

### Testing
```bash
pytest
pytest --cov=app tests/
```

### Code Quality
```bash
black .
flake8
mypy .
```

## Database Setup
```bash
# Create tables
python scripts/create_db.py

# Seed sample data
python scripts/seed_data.py

# Database migrations
alembic upgrade head
```

## Docker Development
```bash
# Start all services
docker-compose -f docker/docker-compose.dev.yml up -d

# View logs
docker-compose -f docker/docker-compose.dev.yml logs -f payment-service

# Stop services
docker-compose -f docker/docker-compose.dev.yml down
```

## Environment Variables
See `.env.example` for required environment variables.

## Project Structure
```
payment-service/
├── app/                 # Main application code
├── tests/              # Test files
├── alembic/            # Database migrations
├── scripts/            # Utility scripts
├── docs/               # Documentation
├── docker/             # Docker configuration
└── requirements.txt    # Dependencies
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run tests and linting
5. Submit a pull request

## License
MIT License
