# Use the official Python 3.13.7 image on Alpine 3.22
FROM python:3.13.7-alpine3.22

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies required for building Python packages
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    git \
    && apk add --no-cache \
    sqlite \
    libstdc++

# Set working directory
WORKDIR /app

# Copy only the files needed for dependency installation
COPY pyproject.toml poetry.lock ./

# Install Poetry and project dependencies
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --only main

# Copy the rest of the application
COPY . .

# Create data directories
RUN mkdir -p /data/raw /data/zim /data/sqlite /data/vectors

# Run the application
CMD ["poetry", "run", "python", "scripts/run_server.py"]

