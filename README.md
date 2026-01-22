# Comments SPA

A backend service for a comment system with support for nested replies, file attachments, real-time updates via 
WebSockets, and basic abuse protection.

The project is intentionally implemented **without user authentication**, as no authorization flow was specified in 
the requirements. The system is designed so that authentication and user-related logic can be added later without 
architectural changes.

---

## Features

* Create and retrieve comments
* Nested replies (threaded comments)
* Pagination for comments and replies
* ORM queries are optimized to avoid N+1 problems using annotations and prefetching
* File attachments:

  * images (with validation and resizing)
  * text files
* CAPTCHA protection for comment creation
* Real-time updates via WebSockets (ASGI)
* HTML sanitization (XSS protection)
* Designed for further scalability (Celery, caching, background tasks)

---

## Tech Stack

* **Django + Django REST Framework** — REST API
* **PostgreSQL** — primary database
* **Redis** — cache and Channels layer
* **Django Channels** — WebSocket support
* **Daphne** — ASGI server
* **Pillow** — image validation and processing
* **Poetry** — dependency management
* **Docker & Docker Compose** — local development environment

---

## Architecture Notes

* The system works **without user accounts** by design.
* CAPTCHA is used to limit automated spam.
* Attachments are validated by:

  * file extension
  * MIME type
  * file size
  * actual content (images verified via Pillow)
* Business logic (file processing, CAPTCHA, WebSocket broadcasting) is separated into a `services` module.
* Redis is used for:

  * CAPTCHA storage
  * Channels communication layer
* WebSocket events broadcast newly created comments to connected clients.

---

## Project Structure

```
comments-spa/
├── apps/                   # Django applications
│   └── comments/           # Comments domain
│   └── core/               # Base models and mixins
├── config/                 # Django & ASGI configuration
├── services/               # Business logic (captcha, ws, file processing)
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Backend image definition
├── manage.py               # Django entry point
├── pyproject.toml          # Poetry configuration
├── poetry.lock             # Dependency lock file
```

---

## Getting Started

All backend-related commands must be executed from:

```
comments-spa/backend/
```

---

## 🐳 Docker Setup (recommended)

1. Copy environment file:

```bash
cp .env.example .env
```

2. (Optional) Adjust variables in `.env`

3. Run the project:

```bash
docker compose up --build
```

Backend will be available at:

* **Admin panel**: [http://localhost:8000/admin/](http://localhost:8000/admin/)
* **API**: [http://localhost:8000/](http://localhost:8000/)

---

## Manual Setup (without Docker)

Requirements:

* Python **3.9.x**
* pip **23.x**
* PostgreSQL 15
* Redis

```bash
python3 -m venv venv
source venv/bin/activate

pip install poetry
poetry install
```

Configure environment variables in `.env`, then run:

```bash
poetry run daphne -b 0.0.0.0 -p 8000 config.asgi:application
```
---

## API Endpoints (brief)

- `GET /comments/` — list root comments (paginated)
- `POST /comments/` — create comment (CAPTCHA required)
- `GET /comments/{id}/` — retrieve comment with attachments
- `GET /comments/{id}/replies/` — list replies for a comment (paginated)
- `GET /captcha/` — generate CAPTCHA
- `WS /ws/comments/` — real-time comment updates

---

## Security Considerations

* HTML input is sanitized to prevent XSS
* SQL injection protection is provided by Django ORM
* CAPTCHA protects comment creation endpoint
* File uploads are strictly validated
* No sensitive data is stored or logged

---

## Possible Future Improvements

* User authentication and authorization
* Rate limiting
* Background processing via Celery
* Object storage for attachments (e.g. S3)
* Advanced caching strategies
* Monitoring and logging infrastructure

These features were intentionally not added to avoid unnecessary complexity and to stay within the scope of the task.

---

## Summary

This project demonstrates:

* clean separation of concerns
* scalable backend architecture
* real-time communication via WebSockets
* secure handling of user-generated content

---

## Scope decisions

Advanced tools such as GraphQL, message brokers, NoSQL databases, and cloud services
were intentionally not included, as they were not required by the task and would
add unnecessary complexity without clear business justification.

The current architecture allows these tools to be integrated later without major refactoring.

---