# Email Queue Service

[![Release](https://img.shields.io/github/v/release/marksxiety/email-queue-service)](https://github.com/marksxiety/email-queue-service/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.8%2B-orange)](https://www.rabbitmq.com/)

A centralized email delivery microservice designed to decouple email-sending from automation systems. Routes all email requests through a single service that handles queuing, reliability, and delivery via SMTP.

## Architecture

```mermaid
graph LR
    subgraph Clients
        A[Automation A]
        B[Automation B]
        C[Automation C]
    end

    subgraph Email Queue Service
        D[API]
        E[(Database)]
        F[RabbitMQ]
        G[Worker]
        H[SMTP Server]
    end

    A --> D
    B --> D
    C --> D
    D -.->| ㅤInsert Pending Emailㅤ | E
    D --> F
    F --> G
    G -.->|ㅤUpdate Email Statusㅤ| E
    G --> H
```

## Features

- **Centralized API** - Single endpoint for all email requests
- **Priority Queues** - High, normal, and low priority email queues
- **Reliability** - RabbitMQ ensures no lost messages

## Prerequisites

- Python 3.8+
- RabbitMQ 3.8+
- SMTP Server

## Setup

### 1. Clone and Install Dependencies

```bash
git clone https://github.com/marksxiety/email-queue-service.git
cd email-queue-service
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

Key configuration sections:
- **API**: Host and port settings
- **RabbitMQ**: Connection credentials and queue names
- **SMTP**: Mail server details

### 3. Start Services

**Start the FastAPI service:**

```bash
py -m app.api_server
```

**Start the worker:**

```bash
py -m app.worker
```

## Usage

### Queue Email Request

**Endpoint:** `POST /api/v1/emails/queue`

**Content-Type:** `multipart/form-data` (required - JSON format not supported)

**Request Body (form-data):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email_type | string | Yes | Type of email (e.g., "welcome", "notification") |
| subject | string | Yes | Email subject line |
| email_template | string | Yes | Template name (without .html extension) |
| email_data | string (JSON) | Yes | Template variables as JSON string |
| priority_level | int | Yes | Priority level (1=high, 2=normal, 3-10=low) |
| attachments | file[] | No | Optional attachment files |

**Example form-data:**

```
email_type: welcome
subject: Welcome to Our Platform
email_template: default_template
email_data: {"name": "John Doe", "company": "Acme Corp"}
priority_level: 1
attachments: [file1.pdf, file2.jpg] (optional)
```

**Response:**

```json
{
  "message": "Email 550e8400-e29b-41d4-a716-446655440000 received and published successfully",
  "data": {
    "email_type": "welcome",
    "subject": "Welcome to Our Platform",
    "email_template": "default_template",
    "email_data": {
      "name": "John Doe",
      "company": "Acme Corp"
    },
    "priority_level": 1
  },
  "email_id": "550e8400-e29b-41d4-a716-446655440000",
  "attachments_processed": 2
}
```

### Priority Levels

- **1**: High priority queue (`email.high`)
- **2**: Normal priority queue (`email.normal`)
- **3-10**: Low priority queue (`email.low`)

## Message Flow

1. Client submits email request via HTTP
2. API validates request
3. Message published to RabbitMQ based on priority
4. Worker consumes from queues (high → normal → low)
5. Email sent via SMTP

## License

[MIT License](./LICENSE).