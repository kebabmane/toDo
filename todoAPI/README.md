# Todo API

This directory contains the Flask backend for the Todo application.

## Running Locally with `uv`

For local development, we recommend using `uv`, a fast Python package installer and resolver.

### Prerequisites

- [uv](https://github.com/astral-sh/uv) must be installed on your system.
- Python 3.11 or higher.

### Setup

1.  **Create a virtual environment:**
    ```bash
    uv venv
    ```

2.  **Activate the virtual environment:**
    ```bash
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    uv pip install -e ".[dev]"
    ```

4.  **Create a `.env` file:**
    Copy the `.env.example` file to `.env` and fill in the required environment variables, such as `SECRET_KEY` and `JWT_SECRET_KEY`.

5.  **Run database migrations:**
    ```bash
    flask db upgrade
    ```

### Running the Application

Once the setup is complete, you can run the application with the following command:

```bash
uv run python app.py
```

The API will be accessible at `http://localhost:5001`.

## Running Tests

The project includes comprehensive test coverage for all API endpoints.

### Prerequisites for Testing

Ensure you have the development dependencies installed:

```bash
uv pip install -e ".[dev]"
```

### Running All Tests

To run the complete test suite:

```bash
pytest
```

### Running Specific Test Files

- **Authentication tests:**
  ```bash
  pytest test_auth.py
  ```

- **Todo management tests:**
  ```bash
  pytest test_todos.py
  ```

- **User management tests (admin endpoints):**
  ```bash
  pytest test_users.py
  ```

- **Database model tests:**
  ```bash
  pytest test_models.py
  ```

- **Integration tests:**
  ```bash
  pytest test_integration.py
  ```

### Test Coverage and Reporting

To run tests with coverage reporting:

```bash
pytest --cov=. --cov-report=html
```

This will generate an HTML coverage report in the `htmlcov/` directory.

### Test Configuration

Tests use an in-memory SQLite database for isolation and speed. The test configuration is managed in `conftest.py` which provides:

- Test Flask application with isolated database
- Authentication fixtures for regular users and admin users
- Sample data fixtures (users, todos, etc.)
- Test client for making API requests

### Test Categories

**Authentication Tests (`test_auth.py`):**
- User registration with validation
- User login and JWT token generation
- Password reset functionality
- Authentication error handling

**Todo Tests (`test_todos.py`):**
- CRUD operations for todos
- Todo filtering and search
- Todo reordering
- User isolation (users can only access their own todos)

**User Management Tests (`test_users.py`):**
- Admin-only user management endpoints
- Role-based access control
- User activation/deactivation
- Admin password reset functionality

**Model Tests (`test_models.py`):**
- Database model validation
- Password hashing and verification
- Model relationships and constraints

**Integration Tests (`test_integration.py`):**
- Full user workflows from registration to todo management
- End-to-end API functionality

## Running with Docker

This project includes a helper script, `run_docker.sh`, to simplify managing the Docker container.

### Prerequisites

- [Docker](https://www.docker.com/get-started) must be installed on your system.
- The script must be executable. Run `chmod +x run_docker.sh` from the `todoAPI` directory.

### Usage

Navigate to the `todoAPI` directory to use the script.

- **Build the image:**
  ```bash
  ./run_docker.sh build
  ```

- **Start the container:**
  ```bash
  ./run_docker.sh start
  ```

- **Stop the container:**
  ```bash
  ./run_docker.sh stop
  ```

- **View logs:**
  ```bash
  ./run_docker.sh logs
  ```

- **Restart the container:**
  ```bash
  ./run_docker.sh restart
  ```

The API will be accessible at `http://localhost:5000`.

### Environment Variables

The `Dockerfile` sets default production environment variables. For local development or to override these, you can use the `-e` flag with the `docker run` command or use a `.env` file.

For example, to run with a different secret key:

```bash
docker run -p 5000:5000 \
  -e SECRET_KEY='my-new-super-secret-key' \
  --name todo-api-container \
  todo-api
```

### Stopping and Removing the Container

To stop the container:

```bash
docker stop todo-api-container
```

To remove the container (after it has been stopped):

```bash
docker rm todo-api-container
