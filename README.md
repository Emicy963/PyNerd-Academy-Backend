# PyNerd - EdTech Platform

![PyNerd Logo](https://via.placeholder.com/150?text=PyNerd+Logo)

[![CI](https://github.com/Start-Up-Angola/pynerd-mvp/actions/workflows/ci.yml/badge.svg)](https://github.com/Start-Up-Angola/pynerd-mvp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-5.0+-green.svg)](https://www.djangoproject.com/)

PyNerd is a robust EdTech platform designed for the Angolan and PALOP markets, focusing on providing high-quality technical education. This repository contains the MVP implementation of the backend API.

## 🚀 Features

- **User Management**: Instructors, Students, and Admins with role-based access control.
- **Course Management**: Create, publish, and manage structured courses with modules and lessons.
- **Learning Experience**: Video lessons, documentation, and progress tracking.
- **Engagement**: Quizzes and certification upon course completion.
- **Secure**: JWT Authentication and secure password handling.

## 🛠️ Tech Stack

- **Backend**: Python, Django, Django REST Framework
- **Database**: PostgreSQL (Production), SQLite (Dev)
- **Documentation**: OpenAPI (Swagger/Redoc)
- **Containerization**: Docker & Docker Compose
- **Testing**: Pytest

## 📦 Installation & Setup

### Prerequisites

- Docker and Docker Compose installed.

### Quick Start (Docker)

1. **Clone the repository:**

   ```bash
   https://github.com/Emicy963/PyNerd-Academy-Backend
   cd pynerd-mvp
   ```

2. **Create a `.env` file** in `PyNerd-Academy-Backend/` (see `.env.example`).

3. **Build and Run:**

   ```bash
   docker-compose up --build
   ```

4. **Access the API:**
   - API Root: http://localhost:8000/api/
   - Swagger UI: http://localhost:8000/api/schema/swagger-ui/

### Local Development (Without Docker)

1. **Navigate to Backend dir:**
   ```bash
   cd PyNerd-Academy-Backend/
   ```
2. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```
3. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```
4. **Run Server:**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
.
├── .github/                # GitHub Actions workflows
├── apps/                   # Django Apps
│   ├── accounts/           # User management & Auth
│   └── courses/            # Course content & progress
├── core/                   # Project settings
├── docs/                   # Documentation
├── docker-compose.yml      # Docker services (DB, Web)
├── Dockerfile              # Application container setup
├── manage.py               # Django entry point
├── pytest.ini              # Test configuration
└── requirements.txt        # Dependencies
```

## 📖 Documentation

- [API Guide](docs/API_GUIDE.md) - Detailed API usage.
- [Changelog](docs/CHANGELOG.md) - Version history.
- [Contributing](CONTRIBUTING.md) - Guidelines for contributors.

## 🤝 Contributing

We welcome contributions! Please check [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## Autor

### Equipe de Desenvolvimento

- **Anderson Cafurica** - *CEO/CTO - Main Developer*
  - GitHub: [@Emicy963](https://github.com/Emicy963)
  - Email: [andersonpaulo931@gmail.com](mailto:andersonpaulo931@gmail.com)
  - LinkedIn: [Anderson Cafurica](https://linkedin.com/in/anderson-cafurica-)

- **Sigeu Fortuna** - *Frontend Lead*

### Equipe de Design

- **Heliand Fortuna** - *Design Lead*

## Contato

If you have any questions, suggestions, or want to contribute to the project, please contact us through GitHub or the contacts of the project leader listed above.
