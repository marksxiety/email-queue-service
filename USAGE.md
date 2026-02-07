# Email Queue API Documentation

A comprehensive guide to queueing emails with dynamic recipients, attachments, and priority-based delivery.

---

## API Endpoint

```
POST /api/v1/emails/queue
```

> **Important:** This endpoint requires `multipart/form-data` content type. JSON format is not supported.

---

## Request Parameters

### Required Fields

**`email_type`** — string  
The type of email being sent (e.g., `welcome`, `notification`, `report`)

**`subject`** — string  
Email subject line

**`email_template`** — string  
Template name without the `.html` extension

**`email_data`** — string (JSON)  
Template variables serialized as a JSON string

**`priority_level`** — integer  
Priority level determining queue assignment:
- `1` → High priority (`email.high` queue)
- `2` → Normal priority (`email.normal` queue)
- `3-10` → Low priority (`email.low` queue)

### Optional Fields

**`to_address`** — string[] (array)  
Dynamic recipient addresses. When provided, overrides default recipients from `email_types` table.

**`cc_addresses`** — string[] (array)  
Carbon copy recipients. Overrides `email_types` defaults when specified.

**`bcc_addresses`** — string[] (array)  
Blind carbon copy recipients. Overrides `email_types` defaults when specified.

**`attachments`** — file[] (array)  
File attachments to include with the email.

---

## Working with Arrays in Form-Data

Since this API uses `multipart/form-data`, array values are sent by repeating the field name with different values.

### Example: Multiple Recipients

```
to_address: user1@example.com
to_address: user2@example.com
to_address: user3@example.com
```

This automatically parses to:
```json
["user1@example.com", "user2@example.com", "user3@example.com"]
```

The same pattern applies to `cc_addresses`, `bcc_addresses`, and `attachments`.

---

## Usage Examples

### Example 1: Basic Email (Using Default Recipients)

Sends an email using recipients defined in the `email_types` table.

```
email_type: welcome
subject: Welcome to Our Platform
email_template: default_template
email_data: {"name": "John Doe", "company": "Acme Corp"}
priority_level: 1
```

---

### Example 2: Override To Recipients

Override the `to_address` field while keeping default CC and BCC from `email_types`.

```
email_type: notification
subject: New Alert
email_template: default_template
email_data: {"alert": "System Update"}
priority_level: 2
to_address: user1@example.com
to_address: user2@example.com
to_address: user3@example.com
```

---

### Example 3: Full Recipient Override

Override all recipient fields (To, CC, and BCC).

```
email_type: notification
subject: Urgent Alert
email_template: default_template
email_data: {"alert": "Critical Update"}
priority_level: 1
to_address: admin1@example.com
to_address: admin2@example.com
cc_addresses: manager@example.com
cc_addresses: lead@example.com
bcc_addresses: audit@example.com
```

---

### Example 4: Email with Attachments

```
email_type: report
subject: Monthly Report
email_template: default_template
email_data: {"month": "January", "year": "2026"}
priority_level: 2
to_address: user@example.com
attachments: [report.pdf]
attachments: [data.xlsx]
```

---

### Example 5: Dynamic Recipients + Attachments

```
email_type: report
subject: Quarterly Report
email_template: default_template
email_data: {"quarter": "Q1 2026"}
priority_level: 1
to_address: executive1@example.com
to_address: executive2@example.com
cc_addresses: team@example.com
attachments: [q1_report.pdf]
attachments: [summary.xlsx]
```

---

## Response Format

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| **201** | Email queued and published successfully |
| **400** | Invalid JSON format or payload validation failed |
| **422** | Email type is not registered in the system |
| **500** | Database insertion failed or queue publishing error |

### Success Response (201 Created)

```json
{
  "success": true,
  "message": "Email 550e8400-e29b-41d4-a716-446655440000 received and published successfully",
  "data": {
    "email_type": "welcome",
    "subject": "Welcome to Our Platform",
    "email_template": "default_template",
    "email_data": {
      "name": "John Doe",
      "company": "Acme Corp"
    },
    "priority_level": 1,
    "to_address": ["user1@example.com", "user2@example.com"],
    "cc_addresses": ["cc@example.com"],
    "bcc_addresses": ["bcc@example.com"]
  },
  "email_id": "550e8400-e29b-41d4-a716-446655440000",
  "attachments_processed": 2
}
```

### Error Response (400 Bad Request)

Invalid JSON in `email_data` field:

```json
{
  "success": false,
  "message": "Invalid JSON format in email_data field",
  "data": null
}
```

Payload validation failed:

```json
{
  "success": false,
  "message": "Payload validation failed: Template 'template.html' does not exist in templates folders: ...",
  "data": null
}
```

### Error Response (422 Unprocessable Entity)

Email type not registered:

```json
{
  "success": false,
  "message": "Email type is not registered"
}
```

### Error Response (500 Internal Server Error)

Database insertion failed:

```json
{
  "success": false,
  "message": "Failed to register the request into email queue",
  "data": null
}
```

Queue publishing failed:

```json
{
  "success": false,
  "message": "Email 550e8400-e29b-41d4-a716-446655440000 inserted but failed to publish to queue",
  "data": {
    "email_type": "welcome",
    "subject": "Welcome to Our Platform",
    "email_template": "default_template",
    "email_data": {
      "name": "John Doe",
      "company": "Acme Corp"
    },
    "priority_level": 1,
    "to_address": ["user1@example.com", "user2@example.com"],
    "cc_addresses": ["cc@example.com"],
    "bcc_addresses": ["bcc@example.com"]
  },
  "email_id": "550e8400-e29b-41d4-a716-446655440000",
  "attachments_processed": 0
}
```

---

## Recipient Merging Logic

The API intelligently merges recipients between your request and the `email_types` table defaults:

| Request `to_address` | Request `cc_addresses` | Final `to_address` | Final `cc_addresses` |
|----------------------|------------------------|--------------------|--------------------|
| ✅ Provided | ✅ Provided | From request | From request |
| ✅ Provided | ❌ Not provided | From request | From `email_types` |
| ❌ Not provided | ✅ Provided | From `email_types` | From request |
| ❌ Not provided | ❌ Not provided | From `email_types` | From `email_types` |

> **Key takeaway:** Each recipient field (to, cc, bcc) can be independently overridden. Fields not specified in the request will fall back to `email_types` table defaults.

---

## Message Processing Flow

```
1. Client Request
   └─> HTTP POST with form-data
   
2. API Validation
   └─> Validates request fields and template existence
   
3. Database Storage
   └─> Message stored with status "Pending"
   
4. RabbitMQ Publishing
   └─> Published to priority-specific queue (high/normal/low)
   
5. Worker Consumption
   └─> Workers consume from queues (high → normal → low priority)
   
6. Recipient Resolution
   └─> Worker fetches final recipients from message payload
   
7. Email Delivery
   └─> Sent via SMTP server
   
8. Status Update
   └─> Database updated to "Sent" or "Failed"
```

---

## Best Practices

**Priority Selection**
- Use priority `1` for time-sensitive emails (alerts, authentication)
- Use priority `2` for standard communications (notifications, updates)
- Use priority `3-10` for bulk or non-urgent emails (newsletters, reports)

**Template Data**
- Ensure `email_data` is valid JSON and properly stringified
- Example: `JSON.stringify({name: "John", company: "Acme"})` 
- Include all variables required by your template
- Test templates with sample data before production use

**Attachments**
- Keep total attachment size reasonable for email delivery
- Only the following file types are supported:
  - **Documents:** PDF, DOC, DOCX, XLS, XLSX, TXT, ZIP
  - **Images:** JPEG, PNG, GIF, BMP, WEBP, TIFF
- Consider file size limits of recipient email servers

**Recipient Management**
- Validate email addresses before submission
- Use BCC for bulk sends to protect recipient privacy
- Leverage `email_types` defaults for consistent routing

---