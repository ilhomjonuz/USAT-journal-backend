# USAT Journal API: Django Project with Docker

## About
This project provides an API for managing journals, articles, authors, and directions within the USAT system. It is containerized using Docker for ease of deployment and scalability.

## Requirements
- Docker
- Docker Compose
- Python 3.10+

## Setting Up the Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/RahimovIlhom/USAT-journal-backend.git
   cd USAT-journal-backend
   ```

2. Create a `.env` file in the root directory with the following content:

   ```bash
   # Django Parameters
   export SECRET_KEY=<your-secret-key>
   export DEBUG=True
   export ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0
   export CSRF_TRUSTED_ORIGINS=<your-csrf-trusted-origins>

   # Docker Container
   export DATABASE_URL=postgres://<your-username>:<your-password>@journal_db:5432/<your-database-name>
   export DJANGO_SUPERUSER_USERNAME=<your-superuser-username>
   export DJANGO_SUPERUSER_EMAIL=<your-superuser-email>
   export DJANGO_SUPERUSER_PASSWORD=<your-superuser-password>

   # Database Parameters
   export POSTGRES_DB=<your-database-name>
   export POSTGRES_USER=<your-username>
   export POSTGRES_PASSWORD=<your-password>
   export POSTGRES_HOST=journal_db
   export POSTGRES_PORT=5432

   # Python Settings
   export PYTHONDONTWRITEBYTECODE=1
   export PYTHONUNBUFFERED=1
   ```

3. Generate a `SECRET_KEY` for Django:
   You can use the following Python script to generate a secure `SECRET_KEY`:
   ```python
   import secrets

   print(secrets.token_urlsafe(50))
   ```
   Copy the output and paste it into the `SECRET_KEY` field in your `.env` file.

## Running the Project

1. Build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```

2. Access the application:
   - API: [http://localhost:8480](http://localhost:8480)

## API Documentation

### Base URL
`http://<your-domain-or-ip>:<port>` (e.g., `http://localhost:8480`)

### Endpoints

#### Journal Endpoints
- **Latest Issues**: `GET /api/v1/journals/latest-issues/`
  - Retrieves the latest journal issues.
- **All Issues**: `GET /api/v1/journals/all-issues/`
  - Retrieves all journal issues.
- **Download Issue**: `GET /api/v1/journals/issue/<id>/download/`
  - Downloads a specific journal issue by ID.
- **Issue Detail**: `GET /api/v1/journals/issue/<slug>/detail/`
  - Retrieves detailed information about a journal issue by its slug.

#### Article Endpoints
- **Submit Article**: `POST /api/v1/articles/submit/`
  - Submits a new article for review.
- **Latest Articles**: `GET /api/v1/articles/latest/`
  - Retrieves the latest articles.
- **All Articles**: `GET /api/v1/articles/all/`
  - Retrieves all articles.
- **Download Article**: `GET /api/v1/articles/<id>/download/`
  - Downloads a specific article by ID.
- **Article Detail**: `GET /api/v1/articles/<slug>/detail/`
  - Retrieves detailed information about an article by its slug.

#### Author Endpoints
- **All Authors**: `GET /api/v1/authors/all/`
  - Retrieves a list of all authors.

#### Direction Endpoints
- **All Directions**: `GET /api/v1/directions/all/`
  - Retrieves a list of all journal directions (categories).

### API Documentation Tools
- **Swagger UI**: [http://localhost:8480/api/docs/swagger/](http://localhost:8480/api/docs/swagger/)
- **ReDoc**: [http://localhost:8480/api/docs/redoc/](http://localhost:8480/api/docs/redoc/)

Authentication is required to access the API documentation. Use your superuser credentials to log in.

## Docker Compose Configuration

The `docker-compose.yml` file includes two services:

### 1. Django API Service (`django_api`)
- Builds the Django application.
- Migrates the database, collects static files, and creates a superuser on startup.
- Runs the application using Gunicorn.

### 2. PostgreSQL Service (`journal_db`)
- Uses the `postgres:14-alpine` image.
- Stores data in a persistent volume `postgres_data`.

Example `docker-compose.yml`:
```yaml
version: '3.9'

services:
  django_api:
    build:
      context: .
    container_name: django_api
    env_file: .env
    ports:
      - "8480:8000"
    volumes:
      - .:/app
      - ./staticfiles:/app/staticfiles
      - ./media:/app/media
    depends_on:
      - journal_db
    command: >
      sh -c "
            python manage.py compilemessages &&
            python manage.py migrate &&
            python manage.py collectstatic --noinput &&
            python manage.py createsuperuser --noinput || echo 'Superuser yaratilmadi.' &&
            gunicorn core.wsgi:application --bind 0.0.0.0:8000"

  journal_db:
    image: postgres:14-alpine
    container_name: journal_db
    env_file: .env
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Additional Notes
- Replace placeholders in the `.env` file with your actual values.
- The API uses DRF and is secured with authentication. Ensure proper credentials are set for accessing restricted endpoints.

Feel free to modify this file to meet your project's needs.
