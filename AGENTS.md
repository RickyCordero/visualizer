# AI Agent Guidelines

This document provides rules and guidelines for AI agents operating within this repository. It defines standard commands, code style, architecture, and project structure to ensure consistency and quality.

## 1. Project Overview & Architecture

This repository contains a real-time visualization system consisting of:
- **Visualizer**: A Django web application (`/visualizer`) that consumes dynamic BPM streams and serves a web frontend.
- **Producer**: A Python script (`/producer`) utilizing `kafka-python` and Ableton Link (via `LinkToPy`) to produce BPM streams.
- **Docker**: Containerized environments for both components, orchestrated via `docker-compose.dev.yml`.

### Key Technologies
- **Python 3.8+**
- **Django 3.2.x** (Web Framework)
- **Apache Kafka** (Event Streaming)
- **Pipenv** (Dependency Management)
- **Server-Sent Events (SSE)** (Real-time updates)

---

## 2. Build, Lint, and Test Commands

Since this project utilizes Pipenv for dependency management, all commands must be executed within the virtual environment or prefixed with `pipenv run`.

### Setup and Dependencies
- **Install dependencies (Visualizer)**: `cd visualizer && pipenv install --dev`
- **Install dependencies (Producer)**: `cd producer && pipenv install --dev`

### Testing
There are currently no explicitly defined test suites, but for standard Django and Python development, use the following:
- **Run all Visualizer tests**:
  ```bash
  cd visualizer && pipenv run python manage.py test
  ```
- **Run a single Visualizer test class**:
  ```bash
  cd visualizer && pipenv run python manage.py test app_name.tests.TestClass
  ```
- **Run a specific Visualizer test method**:
  ```bash
  cd visualizer && pipenv run python manage.py test app_name.tests.TestClass.test_method
  ```

### Linting & Formatting
To maintain PEP8 compliance, agents should adhere to standard Python linting tools. (Ensure these tools are installed if you intend to run them, or suggest adding them to `[dev-packages]`).
- **Format code with Black**:
  ```bash
  pipenv run black .
  ```
- **Sort imports with isort**:
  ```bash
  pipenv run isort .
  ```
- **Lint code with Flake8**:
  ```bash
  pipenv run flake8 .
  ```

### Running the Application (Build & Run)
- **Start the entire stack (Kafka, Zookeeper, Nginx, Django, Producer)**:
  ```bash
  docker-compose -f docker-compose.dev.yml up --build
  ```
- **Run the Django server locally (without Docker)**:
  ```bash
  cd visualizer && pipenv run python manage.py runserver 0.0.0.0:8000
  ```

---

## 3. Code Style Guidelines

All agents modifying code in this project must strictly adhere to the following conventions:

### Formatting & Syntax
- **PEP8 Compliance**: Code must be fully compliant with PEP8 guidelines.
- **Line Length**: Max 88 characters (Black default).
- **Indentation**: 4 spaces per indentation level.
- **Strings**: Use double quotes (`""`) for strings by default (Black standard), and single quotes (`''`) for characters or inner strings.
- **Docstrings**: Use `"""triple double quotes"""` for all docstrings. Follow PEP 257.

### Imports
- Group imports into three sections, separated by a blank line:
  1. Standard library imports (e.g., `import os`, `import sys`).
  2. Related third-party imports (e.g., `import django`, `import kafka`).
  3. Local application/library specific imports.
- Use absolute imports over relative imports wherever possible.
- Avoid wildcard imports (`from module import *`).

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `BpmConsumer`, `VisualizerConfig`).
- **Functions & Methods**: `snake_case` (e.g., `start_stream()`, `process_message()`).
- **Variables**: `snake_case` (e.g., `current_bpm`, `message_payload`).
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `KAFKA_BROKER_URL`, `MAX_RETRIES`).
- **Private Variables/Methods**: Prefix with a single underscore (e.g., `_internal_state`, `_parse_data()`).

### Typing
- Although not currently heavily typed, adding Python Type Hints (`typing` module) to new function signatures and complex variables is **strongly encouraged**.
- Example: `def process_bpm(bpm: int, source: str) -> bool:`

### Error Handling
- Use specific exception classes (e.g., `KeyError`, `kafka.errors.KafkaError`) rather than catching broad `Exception` where possible.
- Include a descriptive error message when raising or logging exceptions.
- **Do not** use silent `try-except-pass` blocks without a comment explaining why the error is ignored.
- Use Python's built-in `logging` module rather than `print()` statements for production or long-running code (like the producer or Django views).

### Django Specific Guidelines
- **Models**: Fat models, skinny views. Put business logic in model methods or service layers, not directly in views.
- **Views**: Prefer Class-Based Views (CBVs) for standard CRUD operations, but function-based views are acceptable for simple or highly custom endpoints (like SSE streams).
- **Migrations**: Always generate and apply migrations when modifying models (`python manage.py makemigrations` and `python manage.py migrate`). Do not check in broken or conflicting migrations.

### Kafka Specific Guidelines
- Ensure proper configuration for serializers/deserializers (e.g., UTF-8 string encoding or JSON serialization).
- Handle connection failures gracefully with retry mechanisms or clear logging.

---

## 4. Agent Tool Usage & Safety

- **Read Before Write**: Always use the `read` or `glob` tools to understand context, surrounding code, and established patterns before using the `write` or `edit` tools.
- **Incremental Changes**: When creating new features, take small, incremental steps and self-verify if possible.
- **No Destructive Operations**: Do not run destructive git commands (e.g., `git reset --hard`) or delete databases/migrations without explicit user confirmation.
- **Absolute Paths**: Always use absolute paths starting with the project root when executing file-system tools.
