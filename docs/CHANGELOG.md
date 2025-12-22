# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2025-12-22

### Added

- **Courses**: Tests for Categories model and related endpoints.

## [1.2.0] - 2025-12-22

### Added

- **Courses**: Categories model and related endpoints.
- **Accounts**: Social auth pipeline for JWT generation.

## [1.1.0] - 2025-12-17

### Added

- **Authentication**: Forgot Password and Reset Password flows.
- **Registration**: Enforced `STUDENT` role for public sign-ups.
- **Dashboard**: `my_courses` endpoint for student enrollments.
- **Assessment**: Quiz API (list quizzes by lesson).
- **Engagement**: Automatic Certificate generation logic.

## [1.0.0] - 2025-12-16

### Added

- **Authentication**:
  - User registration, login, and password management.
  - JWT Authentication (Access & Refresh tokens).
  - Social Login placeholders (Google/GitHub).
  - Account activation via email.
- **Courses**:
  - Course management (CRUD) for Instructors.
  - Module and Lesson management (Polymorphic lessons: Video).
  - Student Enrollment and Progress tracking.
  - Course search and filtering.
- **Documentation**:
  - Swagger/Redoc API documentation via `drf-spectacular`.
  - Comprehensive PEP-compliant docstrings.
- **DevOps**:
  - Docker and Docker Compose setup for development.
  - CI/CD pipeline using GitHub Actions (Linting & Testing).

### Changed

- **Database**:
  - Switched to PostgreSQL for production/Docker environments.
  - Optimized database schema for Courses and Enrollments.
- **Security**:
  - Enhanced permission classes for API endpoints.
  - Sanitized inputs and validated URLs.

### Fixed

- Resolved Timezone configuration issues ("Africa/Luanda").
- Fixed `Lesson` model "order" field inconsistency in tests.
- Corrected API schema generation warnings.
