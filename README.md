# Comments SPA

## Backend

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

## API Endpoints (brief)

```
- GET /comments/ — list root comments (paginated)
- POST /comments/ — create comment (CAPTCHA required)
- GET /comments/{id}/ — retrieve comment with attachments
- GET /comments/{id}/replies/ — list replies for a comment (paginated)
- GET /attachments/{id}/ — retrieve attachment content
- GET /captcha/ — generate CAPTCHA
- WS /ws/comments/ — real-time comment updates
```

---

## Security Considerations

* HTML input is sanitized to prevent XSS
* SQL injection protection is provided by Django ORM
* CAPTCHA protects comment creation endpoint
* File uploads are strictly validated
* No sensitive data is stored or logged

---

## Frontend

The frontend is a single-page application (SPA) responsible for displaying comments, replies, attachments, and handling
user interactions.

## Features

• Display paginated comments and nested replies
• Create new comments and replies
• Client-side validation with inline error display
• File attachment upload with preview before submission:
• image preview
• text file preview
• Attachment viewing via LightBox
• Sorting and pagination controls
• CAPTCHA support
• HTML preview for formatted comment body
• Integration with backend WebSocket events (ready for real-time updates)

## Tech Stack

* **Vue 3 (Composition API)**
* **Vite** — build tool
* **Axios** — HTTP client
* **Tailwind CSS** — styling
* **Docker** — production build

Frontend Structure

```
frontend/
├── src/
│   ├── api/                # Axios instances and API calls
│   ├── components/         # Reusable UI components
│   │   ├── CommentItem.vue
│   │   ├── CommentList.vue
│   │   ├── CommentForm.vue
│   │   ├── CommentAttachments.vue
│   │   ├── CommentsFilter.vue
│   │   ├── PaginationBar.vue
│   │   ├── LightBox.vue
│   ├── views/
│   │   └── CommentsPage.vue
│   ├── App.vue
│   └── main.js
├── index.html
├── vite.config.js
├── package.json
├── package-lock.json
└── Dockerfile
```

## Frontend Build

The frontend is built in a dedicated Docker container and produces static assets.
These assets are mounted into the Nginx container and served directly.

---

## Nginx

Nginx acts as a reverse proxy and static file server.

## Responsibilities

• Serve frontend static assets
• Proxy API requests to the backend
• Proxy WebSocket connections
• Serve Django static files
• Enforce request size limits for file uploads

## Routing

```
 • / — frontend SPA
 • /api/ — backend REST API
 • /ws/ — WebSocket connections
 • /admin/ — Django admin pannel
 • /static/ — Django static files
```

---

## Docker & Docker Compose

The project is fully containerized and can be started with a single command.

## Services

• frontend
• Builds the Vue application
• Outputs static files to a shared volume
• backend
• Django + DRF + Channels
• Runs migrations and collects static files on startup
• postgres
• PostgreSQL database
• redis
• Used for CAPTCHA storage and Channels layer
• nginx
• Reverse proxy and static file server

## Network Isolation

Separate Docker bridge networks are used to limit service visibility:
• backend ↔️ database
• backend ↔️ redis
• backend ↔️ nginx
• frontend ↔️ nginx

Each service can only communicate with the services it directly depends on.

---

## Environment Variables

All configuration is handled via environment variables.
• .env — required, contains actual configuration values
• .env.example — example file with variable definitions

The project will not start without a valid .env file.

---

## Getting Started

The project is designed to be run using Docker and Docker Compose.

Manual (non-Docker) setup is intentionally omitted to avoid environment inconsistencies
and to ensure a reproducible startup process.

```
comments-spa/
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

* **Admin panel**: [http://localhost/admin/](http://localhost/admin/)
* **API**: [http://localhost/api/](http://localhost/api/)

---

### Admin access

To access Django admin panel, create a superuser:

```
  docker compose exec backend python manage.py createsuperuser
```

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