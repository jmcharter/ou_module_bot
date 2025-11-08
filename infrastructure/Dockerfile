FROM python:3.12-slim

WORKDIR /app

# Install UV
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock data/ ./
COPY src/ou_bot ./src/ou_bot

# Install dependencies with UV
RUN uv sync --frozen

# Create entry point script for the continuous bots
COPY infrastructure/docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
