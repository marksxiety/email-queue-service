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
- `idx_email_queues_type`: (email_type) - Optimizes queries by email type
- `idx_email_attachments_queue`: (email_queue_id) - Optimizes queries for filtering attachments by email queue
- `idx_email_attachments_mime`: (mime_type) - Optimizes queries by attachment MIME type

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

    CREATE TABLE email_attachments (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email_queue_id UUID NOT NULL REFERENCES email_queues(id) ON DELETE CASCADE,
        file_name VARCHAR(255) NOT NULL,
        file_path TEXT NOT NULL,
        mime_type VARCHAR(150) NOT NULL,
        file_size BIGINT NOT NULL,
        checksum_sha256 CHAR(64),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Indexes for faster querying
    CREATE INDEX idx_email_queues_status_priority ON email_queues(status, priority_level, created_at);
    CREATE INDEX idx_email_queues_type ON email_queues(email_type);
    CREATE INDEX idx_email_attachments_queue ON email_attachments(email_queue_id);
    CREATE INDEX idx_email_attachments_mime ON email_attachments(mime_type);

```
