import time

from praw.models import Comment, Submission
import structlog

from ou_bot.common.database import ModuleRepository
from ou_bot.reddit_bot.config import AppConfig
from ou_bot.reddit_bot.template_engine import serve_comment_template
from ou_bot.reddit_bot.praw_handler import get_reddit_instance
from ou_bot.reddit_bot.post_scanner import scan_comments

config = AppConfig()

logger = structlog.stdlib.get_logger(__name__)


def handle_comment(comment: Comment, modules: set[str]):
    bound_logger = logger.bind(comment=comment)

    repo = ModuleRepository()
    if repo.has_replied(comment.id):
        return

    ou_modules = repo.find_by_codes(list(modules))

    response_body = serve_comment_template(modules=ou_modules, user=config.praw.username)
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
            response = comment.reply(response_body)
            if response:
                try:
                    repo.add_reply(comment.id)
                except Exception as e:
                    bound_logger.error("Failed to record reply", error=str(e))
                submission: Submission = comment.submission
                bound_logger.info(
                    f"Responded to comment: {comment.id}, of submission: {submission.title}", post=response
                )
                return
            else:
                bound_logger.error(f"Reply failed (attempt {attempt + 1}/{max_attempts})")
        except Exception as e:
            bound_logger.error(
                f"Reddit API error (attempt {attempt + 1}/{max_attempts})", error=str(e), error_type=type(e).__name__
            )

            if "RATELIMIT" in str(e) or "USER_REQUIRED" in str(e):
                break

            if attempt < max_attempts - 1:
                time.sleep(2**attempt)

    bound_logger.error("All reply attempts failed")


def run():
    reddit = get_reddit_instance()
    logger.info("Scanning comments....")
    scan_comments(config.subreddit, reddit, handle_comment)


if __name__ == "__main__":
    run()
