from datetime import datetime

from praw.models import Comment, Message, Submission
import structlog

from ou_bot.common.database import db
from ou_bot.common.ou_module import OUModule
from ou_bot.common.config import DatabaseConfig
from ou_bot.reddit_bot.config import AppConfig
from ou_bot.reddit_bot.template_engine import serve_modules_template
from ou_bot.reddit_bot.praw_handler import get_reddit_instance
from ou_bot.reddit_bot.post_scanner import scan_submissions

config = AppConfig()

logger = structlog.stdlib.get_logger(__name__)


def handle_submission(submission: Submission, modules: set[str]):
    database_config = DatabaseConfig()
    database = db(database_config)
    with database as session:
        ou_modules = session.query_ou_modules(list(modules))
    response_body = serve_modules_template(modules=ou_modules, user=config.praw.username)
    if not response_body:
        logger.error(
            "Rendering of template has failed",
            modules=ou_modules,
            user=config.praw.username,
        )
        return
    response = submission.reply(response_body)
    if not response:
        logger.error("Post two of two has failed")
        return

    post_two: Comment = response
    logger.info(f"Responded to {submission.title}", post=post_two)


def run():
    reddit = get_reddit_instance()
    print("Scanning submissions....")
    scan_submissions(config.subreddit, reddit, handle_submission)
