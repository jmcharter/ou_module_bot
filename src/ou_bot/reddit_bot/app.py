from datetime import datetime

from praw.models import Submission

from ou_bot.common.database import db
from ou_bot.common.ou_module import OUModule
from ou_bot.common.config import DatabaseConfig
from ou_bot.reddit_bot.config import PRAWConfig
from ou_bot.reddit_bot.mako import serve_modules_template
from ou_bot.reddit_bot.praw_handler import get_reddit_instance
from ou_bot.reddit_bot.post_scanner import scan_submissions

config = PRAWConfig()


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

    # post_one = submission.reply(".")
    # post_two = post_one.reply(serve_modules_template(modules=ou_modules, user=config.username))
    post = submission.reply(serve_modules_template(modules=ou_modules, user=config.username))
    # post_one.delete()
    print(f"Responded to {submission.title}")


def run():
    reddit = get_reddit_instance()
    sub = reddit.subreddit("ouhelperbot_testing")
    print("Scanning submissions....")
    scan_submissions("ouhelperbot_testing", reddit, handle_submission)
