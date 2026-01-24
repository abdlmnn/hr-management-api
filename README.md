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
