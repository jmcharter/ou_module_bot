from datetime import datetime

from praw.models import Comment, Submission
import structlog

from ou_bot.common.database import db
from ou_bot.common.ou_module import OUModule
from ou_bot.common.config import DatabaseConfig
from ou_bot.reddit_bot.config import AppConfig
from ou_bot.reddit_bot.mako import serve_modules_template
from ou_bot.reddit_bot.praw_handler import get_reddit_instance
from ou_bot.reddit_bot.post_scanner import scan_submissions

config = AppConfig()

logger = structlog.stdlib.get_logger(__name__)


def handle_submission(submission: Submission, modules: set[str]):
    database_config = DatabaseConfig()
    database = db(database_config)
    ou_modules = []
    with database as session:
        for module in session.query_ou_modules(list(modules)):
            ou_modules.append(
                OUModule(
                    module_code=module[1],
                    module_title=module[2],
                    url=module[3],
                    credits=module[4],
                    ou_study_level=module[5],
                    related_qualifications=module[6].split(","),
                    course_work_includes=module[7].split(","),
                    next_start=datetime.fromisoformat(module[8]),
                    next_end=datetime.fromisoformat(module[9]),
                )
            )

    response = submission.reply(".")
    if not response:
        logger.error("Post one of two has failed")
        return
    post_one: Comment = response
    response_body = serve_modules_template(modules=ou_modules, user=config.praw.username)
    if not response_body or not isinstance(response_body, str):
        logger.error("Rendering of template has failed", modules=ou_modules, user=config.praw.username)
        return
    response = post_one.reply(response_body)
    if not response:
        logger.error("Post two of two has failed")
        return

    post_two: Comment = response
    post_two.mod.distinguish()
    post_one.delete()

    logger.info(f"Responded to {submission.title}", post=post_two)


def run():
    reddit = get_reddit_instance()
    print("Scanning submissions....")
    scan_submissions(config.subreddit, reddit, handle_submission)
