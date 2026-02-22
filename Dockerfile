# =============================================================================
# Stage 1: Builder
# Installs dependencies into an isolated venv that gets copied to final image.
# =============================================================================
FROM python:3.14-slim AS builder

# Don't write .pyc files during the build, keeps the image cleaner
ENV PYTHONDONTWRITEBYTECODE=1

# Install build dependencies needed to compile certain Python packages
# (psycopg2, Pillow, etc. often need these). Drop what you don't need.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create the venv at a path that won't collide with any bind mount
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only the requirements file first so Docker can cache this layer.
# If your requirements don't change, pip install won't re-run on rebuilds.
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# =============================================================================
# Stage 2: Final image
# Copies only the venv and your application code — no build tools included.
# =============================================================================
FROM python:3.14-slim AS final

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Runtime-only system dependencies.
# libpq-dev is needed at runtime for psycopg2; adjust to match your builder deps.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for running the application.
# Running as root inside a container is unnecessary and a security risk.
RUN useradd --create-home --shell /bin/bash appuser

# Copy the venv from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy application code and set ownership to the non-root user in one step.
# Doing this in a single COPY --chown avoids an extra chmod layer.
COPY --chown=appuser:appuser . .

# Create the staticfiles directory as root and give appuser ownership
# before switching to that user
RUN mkdir -p /app/staticfiles && chown appuser:appuser /app/staticfiles

# Switch to non-root user for everything from here on
USER appuser

# Collect static files at build time so the image is self-contained.
# Requires SECRET_KEY to be set; use a dummy value here since collectstatic
# doesn't need the real one. Override via build arg if needed.
ARG DJANGO_SECRET_KEY=build-phase-placeholder
ARG DJANGO_SETTINGS_MODULE=b9_printer_mgmt.settings
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
ENV DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}

RUN python manage.py collectstatic --noinput

# serves on 8000 inside the container.
# Map to whatever host port you like in docker-compose or your reverse proxy.
EXPOSE 8000
