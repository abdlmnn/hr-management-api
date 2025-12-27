# Django REST API

This project is a Django-based REST API using Django REST Framework (DRF).

## Prerequisites

- Python 3.10+
- Docker

## Install Python 3.10

- Install Python 3.10, run the following commands:

```sh
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get install -y python3.10
sudo python3.10 --version
```

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. **Create a virtual environment:**

   ```sh
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   ```sh
   cp .env.dev .env
   ```

   - Fill all the neccessary data inside your .env file

5. **Run database migrations:**
   ```sh
   python manage.py migrate
   ```
6. **Run the development server:**
   ```sh
   python manage.py runserver
   ```

## Running with Docker

1. **Build and start the container:**
   ```sh
   sudo docker-compose build --no-cache
   ```
   ```sh
   sudo docker-compose up -d # detach mode
   ```

# HR Management API

## Install requirements

- Added Django-filter

## Make migrations & Migrate

- python manage.py makemigrations
- python manage.py migrate

## Features

- **JWT Authentication** - Secure token-based authentication
- **Celery Background Tasks** - Asynchronous email notifications
- **Advanced Filtering & Search** - Powerful query capabilities
- **Pagination** - Efficient data loading (100 items per page)
- **File Uploads** - Resume and ID document handling
- **Standardized Error Responses** - Consistent API error handling
- **Comprehensive Validation** - Data integrity checks

## API Endpoints

### Authentication

- `POST /api/token/` - Obtain JWT access and refresh tokens
- `POST /api/token/refresh/` - Refresh expired access tokens

### Jobs Management

- `GET /api/v1/jobs/` - List jobs with filtering/search/pagination
- `POST /api/v1/jobs/` - Create new job posting
- `GET /api/v1/jobs/{id}/` - Retrieve job details
- `PUT /api/v1/jobs/{id}/update/` - Update job information
- `DELETE /api/v1/jobs/{id}/delete/` - Delete job posting

### Applicants Management

- `GET /api/v1/applicants/` - List applications with filtering
- `POST /api/v1/applicants/` - Submit job application (public endpoint)
- `PUT /api/v1/applicants/{id}/update/` - Update application status
- `DELETE /api/v1/applicants/{id}/delete/` - Delete application

### Supporting Endpoints

- `GET /api/v1/departments/` - List departments
- `GET /api/v1/job_types/` - List job types
- `GET /api/v1/notifications/` - List email notifications

## Filtering, Search & Ordering

### Jobs Filtering

- `?department=1` - Filter by department ID
- `?job_type=2` - Filter by job type ID
- `?is_active=true` - Show only active jobs
- `?deadline_before=2024-12-31` - Jobs due before date
- `?deadline_after=2024-01-01` - Jobs due after date

### Ordering

- `?ordering=name` - Sort by job name
- `?ordering=-date_created` - Sort by newest first
- `?ordering=deadline` - Sort by deadline

### Applicants Filtering

- `?status=shortlisted` - Filter by application status
- `?job=1` - Filter by job ID

## Pagination

All list endpoints return paginated results:

```json
{
  "count": 150,
  "next": "http://api.example.com/api/v1/jobs/?page=2",
  "previous": null,
  "results": [...]
}
```
