# Stage 1: Builder
FROM python:3.13-slim-bullseye as builder

WORKDIR /app

# Install system dependencies for building python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management (optional but good since user uses it)
# Or just use pip effectively with wheels
COPY pyproject.toml .
# We'll use pip to install into a virtualenv or user directory for simplicity in the final stage
# Exporting requirements from pyproject.toml is safer for standard docker builds if uv isn't in the final image
# But here let's stick to standard pip wheel building

RUN pip install --upgrade pip
RUN pip install "psycopg2-binary>=2.9.9" "gunicorn>=21.2.0"
# Install dependencies into a temporary directory to copy later
# For simplicity with pyproject.toml without lock file in standard docker:
# We can use uv to export requirements.txt
RUN pip install uv
RUN uv pip compile pyproject.toml -o requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# Stage 2: Final
FROM python:3.13-slim-bullseye

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache /wheels/*

# Copy project files
COPY . .

# Collect static files
# We need SECRET_KEY for collectstatic, a dummy one is fine for build
RUN SECRET_KEY=dummy python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Gunicorn entrypoint
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
