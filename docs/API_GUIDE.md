# PyNerd API Guide

PyNerd provides a RESTful API built with Django REST Framework. This guide provides a quick overview of how to interact with the API.

## Interactive Documentation

We provide interactive API documentation via Swagger UI and Redoc.

- **Swagger UI**: `/api/schema/swagger-ui/`
  - Interactive testing of endpoints.
- **Redoc**: `/api/schema/redoc/`
  - Clean, organized reference documentation.

## Authentication

The API uses **JWT (JSON Web Token)** for authentication.

### 1. Register

`POST /api/auth/register/`

```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "role": "STUDENT"
}
```

### 2. Login (Get Token)

`POST /api/token/`

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**

```json
{
  "access": "eyJ0eX...",
  "refresh": "eyJ0eX..."
}
```

### 3. Using the Token

Include the access token in the `Authorization` header of subsequent requests:

```
Authorization: Bearer <your_access_token>
```

## Key Endpoints

### Accounts

- `GET /api/users/profile/`: Get current user profile.
- `POST /api/users/change_password/`: Change password.

### Courses

- `GET /api/courses/`: List available courses.
- `GET /api/courses/{slug}/`: Get course details.
- `POST /api/courses/{id}/enroll/`: Enroll in a course (Student only).

### Progress

- `PATCH /api/progress/{id}/`: Update lesson completion status.

## Error Handling

Standard HTTP status codes are used:

- `200 OK`: Success.
- `201 Created`: Resource created.
- `400 Bad Request`: Validation error.
- `401 Unauthorized`: Authentication failed or missing.
- `403 Forbidden`: Permission denied.
- `404 Not Found`: Resource not found.
- `500 Internal Server Error`: Server error.
