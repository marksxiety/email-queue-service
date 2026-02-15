# Setup Guide

This guide will help you set up and run the Email Queue Service.

---

## Prerequisites

Ensure you have the following installed:
- **Python** 3.8 or higher
- **RabbitMQ** 3.8 or higher
- **PostgreSQL** database
- **SMTP Server** (Gmail, SendGrid, etc.)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/marksxiety/email-queue-service.git
cd email-queue-service
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install python-magic (for file attachment security)

The service uses `python-magic` to detect file types via magic bytes for security.

**Linux/macOS:**
```bash
pip install python-magic
# On Ubuntu/Debian, you may need:
sudo apt-get install libmagic1
```

**Windows:**
```bash
pip install python-magic-bin
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True

# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/

# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=email_queue
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
DATABASE_URL=postgresql://postgres:your-password@localhost:5432/email_queue

# Upload Configuration
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# Rate Limiting Configuration
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100
RATE_LIMIT_GLOBAL_PER_MINUTE=500
RATE_LIMIT_GLOBAL_PER_HOUR=5000
RATE_LIMIT_GRACE_PERIOD_SECONDS=300

# Email Queues
EMAIL_QUEUE_HIGH=email.high
EMAIL_QUEUE_NORMAL=email.normal
EMAIL_QUEUE_LOW=email.low
```

### 5. Initialize the database

See **[DATABASE.md](./app/database/DATABASE.md)** for migration instructions.

---

## Running the Service

### Start the API server:

```bash
python -m app.api_server
```

The API will be available at `http://localhost:8000`

### Start the worker (in a separate terminal):

```bash
python -m app.worker
```

The worker will begin consuming messages from RabbitMQ queues.

---

## Docker Setup (Optional)

If you prefer using Docker:

```bash
# Build the image
docker build -t email-queue-service .

# Run the API server
docker run -p 8000:8000 --env-file .env email-queue-service python -m app.api_server

# Run the worker
docker run --env-file .env email-queue-service python -m app.worker
```

---

## Troubleshooting

### python-magic import errors

If you encounter import errors with `magic`:

- **Linux/macOS**: Ensure `libmagic` is installed (`apt-get install libmagic1` on Ubuntu)
- **Windows**: Use `pip install python-magic-bin` instead of `python-magic`

### RabbitMQ connection issues

- Ensure RabbitMQ is running: `rabbitmq-server` (Linux/macOS) or via Windows Services
- Verify connection settings in `.env` file

### Database connection issues

- Ensure PostgreSQL is running
- Verify database credentials and that the database exists
- Check that `DATABASE_URL` matches your PostgreSQL setup

---

## Configuration Reference

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |
| `UPLOAD_DIR` | Directory for uploaded files | `uploads` |
| `MAX_FILE_SIZE` | Maximum file size in bytes (10MB) | `10485760` |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | `True` |
| `RATE_LIMIT_PER_MINUTE` | Requests per minute per IP | `10` |
| `RATE_LIMIT_PER_HOUR` | Requests per hour per IP | `100` |

See `app/config.py` for all available configuration options.
