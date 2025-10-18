FROM python:3.12-slim

WORKDIR /app

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.8.4 \
    POETRY_HOME=/opt/poetry

ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright system dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    libatspi2.0-0 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -
RUN pip install poetry
RUN poetry --version

# Copy project files
COPY pyproject.toml poetry.lock data/ ./
COPY src/ou_bot ./src/ou_bot

# Configure Poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Install Playwright browsers
RUN python -m playwright install chromium

# Create entry point script for the continuous bots
COPY infrastructure/docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
