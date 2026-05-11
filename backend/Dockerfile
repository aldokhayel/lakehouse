# backend/Dockerfile
# Builds the FastAPI backend. Uses a stub app/__init__.py so pip can run
# the editable install before the real source is copied in — preserving
# the Docker layer cache for dependency installs.

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only the project manifest first so the dependency layer is cached
# independently of source changes.
COPY pyproject.toml .

# Editable install requires the package directory to exist.
# Create a minimal stub; the real source is copied below.
RUN mkdir -p app && touch app/__init__.py

RUN pip install --no-cache-dir -e ".[dev]"

# Now copy the full source (overwrites the stub)
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
