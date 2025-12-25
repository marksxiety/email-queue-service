# Email Queue Service

`email-queue-service` is a centralized email delivery microservice designed to remove email-sending responsibilities from individual automation systems. Instead of embedding SMTP logic inside every project, all email requests are routed through a single service that manages templates, queuing, reliability, and delivery.

This service allows automations to focus purely on business logic while email delivery is handled asynchronously, safely, and consistently.

## Conceptual Setup

The service is designed around a simple message flow where multiple clients submit email requests to a centralized service, which then delivers emails via a queue and SMTP provider.

```txt
Automation A ─┐
Automation B ─┼──> email-queue-service ──> RabbitMQ ──> Worker ──> SMTP
Automation C ─┘
```

### Flow Description

1. Multiple automation systems generate email requests.
2. Requests are sent to `email-queue-service` via HTTP.
3. The service validates the request and prepares the email content.
4. The request is then pushed into RabbitMQ for safe, buffered processing.
5. A worker consumes queued messages and sends the emails using SMTP.
