# Improvement Tasks Checklist

Date: 2025-09-24 23:08

Note: Each item is actionable and starts with a checkbox. Complete items can be checked as [x]. The order is designed to go from foundations, through architecture and quality, to delivery.

1. [ ] Establish project foundations and housekeeping
   - [ ] Create a README with setup, run, and deployment instructions (local and Render). 
   - [ ] Add a CONTRIBUTING guide (coding style, branching, commit message conventions). 
   - [ ] Add a CODE_OF_CONDUCT and LICENSE appropriate for the project. 
   - [ ] Add .gitignore entries for Python, Flask, SQLite artifacts (e.g., __pycache__, .pytest_cache, *.pyc, instance/, .env, data/*.db). 

2. [ ] Configuration and secrets management
   - [ ] Move hard-coded admin credentials (ADMIN_USERNAME, ADMIN_PASSWORD) to environment variables with sane defaults for development. 
   - [ ] Replace SECRET_KEY hardcode with environment variable and secure generation guidance. 
   - [ ] Add a config module (e.g., config.py) with Development/Production classes and use app.config. 
   - [ ] Load configuration from environment using python-dotenv in development. 

3. [ ] Security improvements
   - [ ] Store ADMIN_PASSWORD as a salted hash at rest (not a plain hard-coded string). 
   - [ ] Use werkzeug.security (generate_password_hash/check_password_hash) rather than manual sha256. 
   - [ ] Enforce HTTPS cookies in production (SESSION_COOKIE_SECURE, SESSION_COOKIE_SAMESITE, SESSION_COOKIE_HTTPONLY). 
   - [ ] Rate-limit sensitive endpoints (/admin login) to mitigate brute force (e.g., Flask-Limiter). 
   - [ ] CSRF protection for form POSTs (Flask-WTF or custom token). 
   - [ ] Validate and sanitize all request inputs beyond simple .isdigit (e.g., type casting with error handling). 

4. [ ] Application architecture and modularization
   - [ ] Split monolithic app.py into package structure (e.g., app/__init__.py, app/routes/*.py, app/db.py, app/i18n.py). 
   - [ ] Create Blueprints for public, admin, and API routes. 
   - [ ] Centralize database access helpers and context management with connection lifecycle handling. 
   - [ ] Introduce a Services layer (queue service, settings service) to decouple business logic from routes. 
   - [ ] Add error handlers (404, 500) and JSON error responses for API. 

5. [ ] Database layer and migrations
   - [ ] Define schema in migration files (e.g., Flask-Migrate with Alembic) rather than inline DDL. 
   - [ ] Add indexes to frequently queried columns (queue.status, queue.timestamp, queue.ticket_number). 
   - [ ] Add constraints and validation at DB level (CHECK for status values). 
   - [ ] Provide a data retention/cleanup strategy (archiving seated/cancelled after N days). 

6. [ ] Internationalization (i18n) enhancements
   - [ ] Move TRANSLATIONS out of code into JSON/PO files or a dedicated module. 
   - [ ] Add translation keys coverage tests to avoid missing keys. 
   - [ ] Ensure RTL/LTR is applied consistently, including in admin dropdown menus (current hidden menu behavior). 
   - [ ] Add language selection persistence and explicit URL patterns if needed (/en, /ar). 

7. [ ] Input validation and API contract
   - [ ] Define request/response schemas using pydantic or marshmallow for /api/* endpoints. 
   - [ ] Return consistent error codes and messages (structured JSON with code, message, details). 
   - [ ] Add bounds for party_size (e.g., 1..20) and type checking with descriptive errors. 
   - [ ] Validate status transition rules (e.g., waiting -> called -> seated; disallow invalid jumps). 

8. [ ] Observability and logging
   - [ ] Add structured logging (JSON logs) with request IDs and correlation. 
   - [ ] Log authentication failures (without sensitive data) and admin actions (auditing). 
   - [ ] Configure log levels per environment; avoid debug logs in production. 

9. [ ] Performance and robustness
   - [ ] Ensure DB connections are properly closed via context managers; consider connection pooling if moving beyond SQLite. 
   - [ ] Avoid SELECT * patterns; select only required fields. 
   - [ ] Add pagination or limits for queue endpoints if the dataset can grow. 
   - [ ] Guard against race conditions when issuing new ticket numbers (e.g., use a separate sequence or transaction with locking). 

10. [ ] Front-end and UX improvements
    - [ ] Extract inline scripts to static files and add integrity/caching headers. 
    - [ ] Add proper accessible labels, aria attributes, and focus states. 
    - [ ] Fix the admin language menu toggle (currently always hidden); implement a click-to-toggle behavior. 
    - [ ] Add loading and error states for API calls on all pages. 
    - [ ] Provide a way for customers to cancel their ticket (with confirmation) via API. 

11. [ ] Testing strategy
    - [ ] Set up pytest and testing configuration. 
    - [ ] Add unit tests for services (queue issuance, status transitions, settings updates). 
    - [ ] Add API tests using Flask test client (auth, validation, happy paths, error cases). 
    - [ ] Add template rendering tests for both languages (basic smoke tests). 

12. [ ] Continuous Integration (CI)
    - [ ] Add GitHub Actions workflow (lint, test, type-check). 
    - [ ] Cache dependencies and run matrix for multiple Python versions. 

13. [ ] Code quality and consistency
    - [ ] Apply a formatter (Black) and import sorter (isort). 
    - [ ] Add flake8/ruff for linting and fix issues. 
    - [ ] Introduce type hints and mypy; annotate key functions and services. 
    - [ ] Add pre-commit hooks to enforce style and security checks (bandit). 

14. [ ] Deployment and operations
    - [ ] Review render.yaml to ensure environment variables and gunicorn entrypoint are set (avoid Flask dev server in production). 
    - [ ] Add a Procfile or start command for production (gunicorn "app:create_app()" or similar after refactor). 
    - [ ] Document zero-downtime deploy and rollback strategy. 

15. [ ] Feature enhancements (optional, post-foundation)
    - [ ] Add QR code generation for customer join URL directly in admin page (server-side or client-side). 
    - [ ] Add WebSocket/SSE for real-time updates instead of polling. 
    - [ ] Add role-based admin accounts persisted in DB. 
    - [ ] Add analytics dashboard (average wait time, throughput). 

16. [ ] Documentation
    - [ ] Create API reference (endpoints, request/response schemas, examples). 
    - [ ] Architecture overview diagram and narrative. 
    - [ ] Operations runbook (env vars, migrations, backups, monitoring). 


## Security configuration notes (update)
- ADMIN_PASSWORD_HASH: In production, always supply a precomputed hash (use Werkzeug generate_password_hash). The method is embedded in the hash.
- ADMIN_PASSWORD_METHOD: Optional. When ADMIN_PASSWORD_HASH is NOT set and the app needs to derive a dev hash from ADMIN_PASSWORD, the app will use this method. Default: pbkdf2:sha256. This avoids environments where hashlib.scrypt is unavailable.
  - Allowed examples: pbkdf2:sha256 (default), pbkdf2:sha512, scrypt (only if your Python has hashlib.scrypt).
- SECRET_KEY should be provided via environment. The app will generate a random key if absent (OK for dev only).
- Recommended env examples:
  - ADMIN_USERNAME=admin
  - ADMIN_PASSWORD=password123 (dev only)
  - ADMIN_PASSWORD_METHOD=pbkdf2:sha256 (dev safe)
  - ADMIN_PASSWORD_HASH=<use generate_password_hash offline for prod>
  - SESSION_COOKIE_SECURE=true (when behind HTTPS)
  - SESSION_COOKIE_SAMESITE=Lax
  - SESSION_COOKIE_HTTPONLY=true
