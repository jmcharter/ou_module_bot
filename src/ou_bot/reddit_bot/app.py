from datetime import datetime
import praw

from ou_bot.common.database import db
from ou_bot.common.ou_module import OUModule
from ou_bot.module_scraper.config import DatabaseConfig
from ou_bot.reddit_bot.config import PRAWConfig
from ou_bot.reddit_bot.mako import serve_modules_template


def run():
    config = PRAWConfig()
    reddit = praw.Reddit(
        client_id=config.client_id,
        client_secret=config.client_secret,
        password=config.password,
        user_agent=config.user_agent,
        username=config.username,
    )

    sub = reddit.subreddit("ouhelperbot_testing")
    # sub.submit("Test 1", selftext=serve_module_table())

    database_config = DatabaseConfig()
    database = db(database_config)
    ou_modules = []
    with database as session:
        for module in session.query_ou_modules(["M269", "TM111", "MU123"]):
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
    sub.submit(f"Test 5", selftext=serve_modules_template(modules=ou_modules, user=config.username))
