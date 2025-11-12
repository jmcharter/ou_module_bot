# OU Helper Bot

A Reddit bot for r/OpenUniversity that automatically responds to posts and comments mentioning Open University module codes with relevant module information.

## Overview

This bot monitors the r/OpenUniversity subreddit and automatically replies when it detects OU module codes (e.g., TM112, M250). It provides module details including title, description, level, credits, and study time directly from the Open University website.

The system consists of three components:
- **Submission Bot**: Monitors new submissions for module codes
- **Comment Bot**: Monitors comments for module codes
- **Module Scraper**: Weekly scraper that updates the local database with current module information

## Prerequisites

- Docker and Docker Compose
- Reddit API credentials (client ID, client secret, username, password)
- Python 3.12 (for local development)

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# Reddit API credentials
CLIENT_ID=your_reddit_client_id
CLIENT_SECRET=your_reddit_client_secret
REDDIT_USERNAME=your_bot_username
REDDIT_PASSWORD=your_bot_password
REDDIT_USER_AGENT=ou_module_bot/1.0

# Bot configuration
SUBREDDIT=OpenUniversity
MAX_RETRY_ATTEMPTS=5
MAX_CONCURRENT_WORKERS=10

# Template configuration
MAKO_TEMPLATE_DIR=src/ou_bot/reddit_bot/templates
MAKO_MODULE_DIR=data/mako_modules

# Data source
OU_MODULE_URL=https://enrolment.open.ac.uk/page-data/courses/qualifications/page-data.json
DATABASE_NAME=data/ou_modules.db
```

## Running with Docker

Start all services:

```bash
docker-compose up -d
```

This will start:
- Both Reddit bots (submission and comment scanners)
- Module scraper that runs weekly
- Ofelia scheduler to manage scraping intervals

View logs:

```bash
docker-compose logs -f bots
docker-compose logs -f scraper
```

Stop all services:

```bash
docker-compose down
```

## Local Development

Install dependencies using UV:

```bash
pip install uv
uv sync
```

Run individual components:

```bash
# Run submission bot
uv run submission_bot

# Run comment bot
uv run comment_bot

# Run module scraper
uv run module_scraper
```

Format code:

```bash
uv run black src/
```

Run tests:

```bash
uv run pytest tests/
```

## How It Works

### Bot Workflow

1. Bots continuously scan the configured subreddit for new submissions and comments
2. When a post contains an OU module code pattern (e.g., TM112, M250), the bot detects it
3. Bot queries the local SQLite database for module information
4. Response is formatted using Mako templates
5. Bot replies to the post/comment with formatted module details

### Module Scraper

1. Fetches the complete list of OU modules adhering to the websites `robots.txt`
2. Scrapes detailed information for each module using concurrent requests
3. Stores or updates module data in the SQLite database
4. Runs weekly via Ofelia scheduler to keep data current

### Error Handling

- Retry logic with exponential backoff for Reddit API failures
- Rate limit detection and graceful handling
- Structured logging for monitoring and debugging

## Database Schema

The bot uses SQLite to store module information. Data is automatically created and managed by the scraper.

## Templates

Response templates are located in `src/ou_bot/reddit_bot/templates/`. The bot uses different templates for:
- Submission responses (detailed format)
- Comment responses (compact format)
- Module data tables

## Troubleshooting

**Bot not responding:**
- Check Reddit API credentials in `.env`
- Verify bot account has sufficient karma
- Check logs for rate limiting errors

**Scraper failing:**
- Verify `OU_MODULE_URL` is accessible
- Check network connectivity
- Review logs for parsing errors

**Database errors:**
- Ensure `data/` directory exists and is writable
- Check database file permissions

## License

See [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and formatting
5. Submit a pull request
