## Database Schema

### Tables

#### `email_types`

Stores email type configurations including default recipient addresses.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier for the email type |
| type | VARCHAR(100) | NOT NULL, UNIQUE | Email type name (e.g., "welcome", "notification") |
| to_address | TEXT[] | | Default recipient email addresses array |
| cc_addresses | TEXT[] | | Default CC email addresses array |
| bcc_addresses | TEXT[] | | Default BCC email addresses array |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when the email type was created |

#### `email_queues`

Stores queued emails waiting to be sent.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier for the email queue entry |
| sender | VARCHAR(100) | NOT NULL | Sender identifier |
| email_type | VARCHAR(100) | NOT NULL, REFERENCES email_types(type) | Email type reference |
| subject | VARCHAR(500) | NOT NULL | Email subject line |
| email_template | VARCHAR(100) | | Template file name |
| email_data | JSONB | | Dynamic email content data |
| priority_level | SMALLINT | DEFAULT 5, CHECK (1-10) | Email priority (1=highest, 10=lowest) |
| status | SMALLINT | NOT NULL, DEFAULT 0, CHECK (0-2) | Email status: 0=Pending, 1=Sent, 2=Failed |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when queued |
| sent_at | TIMESTAMP | | Timestamp when email was sent |

### Indexes

- `idx_email_queues_status_priority`: (status, priority_level, created_at) - Optimizes queries for filtering by status and priority
- `idx_email_queues_sender`: (sender) - Optimizes queries by sender
- `idx_email_queues_type`: (email_type) - Optimizes queries by email type

## SQL Schema

```sql
    CREATE TABLE email_types (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        type VARCHAR(100) NOT NULL UNIQUE,
        to_address TEXT[],
        cc_addresses TEXT[],
        bcc_addresses TEXT[],
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE email_queues (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        sender VARCHAR(100) NOT NULL,
        email_type VARCHAR(100) NOT NULL REFERENCES email_types(type),
        subject VARCHAR(500) NOT NULL,
        email_template VARCHAR(100),
        email_data JSONB,
        priority_level SMALLINT DEFAULT 5,
        status SMALLINT NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        sent_at TIMESTAMP,
        CONSTRAINT valid_status CHECK (status BETWEEN 0 AND 2),
        CONSTRAINT valid_priority CHECK (priority_level BETWEEN 1 AND 10)
    );

    -- Indexes for faster querying
    CREATE INDEX idx_email_queues_status_priority ON email_queues(status, priority_level, created_at);
    CREATE INDEX idx_email_queues_sender ON email_queues(sender);
    CREATE INDEX idx_email_queues_type ON email_queues(email_type);

```
