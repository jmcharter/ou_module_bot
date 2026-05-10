import time

from praw.models import Submission
import structlog

from ou_bot.common.database import ModuleRepository
from ou_bot.reddit_bot.config import AppConfig
from ou_bot.reddit_bot.template_engine import serve_modules_template
from ou_bot.reddit_bot.praw_handler import get_reddit_instance
from ou_bot.reddit_bot.post_scanner import scan_submissions

config = AppConfig()

logger = structlog.stdlib.get_logger(__name__)


def handle_submission(submission: Submission, modules: set[str]):
    bound_logger = logger.bind(submission=submission)

    ou_modules = ModuleRepository().find_by_codes(list(modules))

    response_body = serve_modules_template(modules=ou_modules, user=config.praw.username)
    if not response_body:
        bound_logger.error(
            "Rendering of template has failed",
            modules=ou_modules,
            user=config.praw.username,
        )
        return

    max_attempts = config.max_retry_attempts
    for attempt in range(max_attempts):
        try:
            response = submission.reply(response_body)
            if response:
                bound_logger.info(f"Responded to {submission.title}", post=response)
                return
            else:
                bound_logger.error(f"Reply failed (attempt {attempt + 1}/{max_attempts})")
        except Exception as e:
            bound_logger.error(
                f"Reddit API error (attempt {attempt + 1}/{max_attempts})",
                error=str(e),
                error_type=type(e).__name__
            )

            if "RATELIMIT" in str(e) or "USER_REQUIRED" in str(e):
                break

            if attempt < max_attempts - 1:
                time.sleep(2 ** attempt)

    bound_logger.error("All reply attempts failed")


def run():
    reddit = get_reddit_instance()
    logger.info("Scanning submissions....")
    scan_submissions(config.subreddit, reddit, handle_submission)


run()
