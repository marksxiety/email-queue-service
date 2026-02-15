# Changelog

All notable changes to this project will be documented in this file.

## [1.3.1] - 2026-02-15

### Security Fixes
- Fixed path traversal vulnerability - filenames are now sanitized to prevent directory traversal attacks (e.g., ../../../etc/passwd)
- Fixed spoofed MIME type vulnerability - file types are now detected using magic bytes instead of trusting client-provided headers
- Added file extension whitelist validation to prevent uploading disallowed file types
- Added file size limit enforcement to prevent denial-of-service attacks (default 10MB)
- Added null filename validation to prevent errors with missing attachment filenames

### Configuration
- Added `ALLOWED_EXTENSIONS` set in `app/config.py` for file extension whitelist
- Added `MAX_FILE_SIZE` environment variable in `app/config.py` (default 10MB)
- Enhanced `ALLOWED_MIME_TYPES` with comprehensive file type coverage

### Documentation
- Created `SETUP.md` for installation and setup
- Restructured `README.md` to focus on overview, architecture, and key features
- Added file attachment security documentation
- Moved file attachment configuration to `USAGE.md`

---

## [1.3.0] - 2026-02-08

### Added
- Retry mechanism in case the worker fails to process emails
- Rate limiting functionality for API endpoints
- Rate limiting configuration support
- Email type validation to verify if email type is registered in database before processing
- Database query function to verify email type existence
- Unit tests for rate limiting and email type validation
- Mock testing for API responses
- Unit tests for rate limiting response
- Unit testing libraries and httpx dependency for TestClient in GitHub Actions

### Changed
- Clarified API service scope - available for any software, not limited to automations
- Updated documentation with testing configuration and expected HTTP status codes
- Used Open API standards for response HTTP status codes

---

## [1.2.1] - 2026-01-13

### Added
- Unit tests for publish_to_rabbitmq function covering various priority levels
- Unit tests for get_file_attachments function covering various scenarios
- Unit tests for email queue database transactions
- Unit tests for calculate_sha256 function
- Unit tests for render_email_template function
- Unit tests for parse_address_value function
- Unit and integration tests for print_logging and get_logger functions
- Connection testing with proper error handling
- GitHub Actions workflow for running tests and coverage
- Unit testing documentation and instructions
- Test coverage badge in README

### Removed
- Unused modules and folders

### Changed
- Reordered badges in README for improved visibility
- Updated documentation links

---

## [1.2.0] - 2026-01-11

### Added
- Optional parameters for to, cc, and bcc addresses in email payload
- Dynamic recipient override functionality allowing to, cc, and bcc in payload to override queried recipients from email_types

### Changed
- Separated usage instructions for endpoint and payload approaches
- Updated main documentation to display project purpose and architecture

---

## [1.1.0] - 2026-01-09

### Added
- File attachment handling for emails queued with attachment data
- Function to fetch email attachment details via email ID

### Changed
- Modularized functions and created separate utility files for easier maintenance
- Updated filename handling for uploads path
- Updated documentation with library versions

---

## [1.0.0] - 2026-01-08

### Added
- Initial release of email queue service
- API endpoint for email queue operations
- Worker service for processing queued emails
- PostgreSQL database integration
- RabbitMQ message queue support
- Email template rendering with Jinja2
- File attachment support with MIME type validation
- Email type management with recipient configuration
- Dynamic To, Cc, and Bcc recipients support
- Database schema and migration scripts
- Environment-based configuration system
- Logging utilities
- SHA256 file hash calculation
- Email address parsing utilities
- API and worker process execution scripts
- MIT License
