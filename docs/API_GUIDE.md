# PyNerd API Guide & Frontend Integration

This guide details how to integrate the PyNerd Backend API with the frontend application.

## 📚 Documentation

- **Swagger UI**: [`/api/schema/swagger-ui/`](http://localhost:8000/api/schema/swagger-ui/) - Interactive testing.
- **Redoc**: [`/api/schema/redoc/`](http://localhost:8000/api/schema/redoc/) - API Reference.

## 🔐 Authentication

### 1. Registration

**Endpoint**: `POST /api/auth/register/`

The backend generates a unique `username` if not provided. **Note**: Public registration always creates a user with `role="STUDENT"`.

```json
{
  "username": "coolnerd", // Optional (backend can generate)
  "email": "student@pynerd.com",
  "password": "strongPassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

### 2. Account Activation

After registration, the user receives an email with a link:
`http://localhost:8000/api/auth/activate/{uid}/{token}/`

**Frontend Flow**:

1. User clicks the link in email.
2. If the link points to frontend, the frontend should extract `uid` and `token` and call:
   **GET** `/api/auth/activate/{uid}/{token}/`
3. If successful (`200 OK`), redirect user to Login page.

### 3. Login (Dual Auth)

**Endpoint**: `POST /api/auth/login/`

Supports login via **Username** or **Email**. Send the value in the `username` field.

```json
{
  "username": "student@pynerd.com", // OR "coolnerd"
  "password": "strongPassword123!"
}
```

**Response**:

```json
{
  "access": "eyJ0eX...",
  "refresh": "eyJ0eX...",
  "role": "STUDENT"
}
```

### 4. Password Recovery

**Request Reset**: `POST /api/auth/password-reset/`

```json
{ "email": "student@pynerd.com" }
```

Sends an email with a recovery link containing `{uid}` and `{token}`.

**Confirm Reset**: `POST /api/auth/password-reset-confirm/{uid}/{token}/`

```json
{ "new_password": "newStrongPassword123!" }
```

### 5. Social Login (Google/GitHub)

We use `drf-social-oauth2`.

**Endpoint**: `POST /api/auth/convert-token`

**Payload**:

```json
{
  "grant_type": "convert_token",
  "client_id": "<YOUR_CLIENT_ID>",
  "client_secret": "<YOUR_CLIENT_SECRET>",
  "backend": "google-oauth2", // or "github"
  "token": "<USER_ACCESS_TOKEN_FROM_PROVIDER>"
}
```

## 📚 Courses

### 1. List Courses

**Endpoint**: `GET /api/courses/`

**Filters**:

- `?category=Programming`: Filter by category.
- `?search=Python`: Search title/description/instructor.

**Response**:
Returns a paginated list of published courses.

### 2. My Courses (Dashboard)

**Endpoint**: `GET /api/courses/my_courses/`
Requires `Authentication`. Returns courses the student is enrolled in.

### 3. Enrollment

**Endpoint**: `POST /api/courses/{id}/enroll/`
Requires `Authentication`.

### 4. Quizzes (Assessment)

**Endpoint**: `GET /api/quizzes/?lesson_id={id}`
Requires `Authentication`. Returns quizzes for a specific lesson.

## 🏆 Certificates

Certificates are **automatically generated** when a student completes all lessons in a course (100% progress).
Frontend does not need to explicitly call "generate". Just check for existence or list via user profile.

## 🔄 Common Errors

- `400 Bad Request`: Check `username` field in Login.
- `401 Unauthorized`: Token expired or invalid credentials.
