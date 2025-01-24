from typing import Callable, Optional

from cachetools.func import ttl_cache
from praw import Reddit

from ou_bot.common.config import DatabaseConfig
from ou_bot.common.database import db

MODULES_TTL = 24 * 60 * 60  # 24 Hours


@ttl_cache(ttl=MODULES_TTL)
def get_tma_modules() -> list[str]:
    database_config = DatabaseConfig()
    database = db(database_config)
    with database as session:
        modules_codes = session.get_all_module_codes()
        return [module_code[0] for module_code in modules_codes]


def match_found(target: str, module: str) -> bool:
    return module.upper() in target.upper()


def get_matching_modules_from_string(target: str) -> Optional[set[str]]:
    modules = get_tma_modules()
    return set(module for module in modules if match_found(target, module))


def scan_submissions(sub_name: str, reddit: Reddit, submission_handler: Callable[[str], None]):
    subreddit = reddit.subreddit(sub_name)
    for submission in subreddit.stream.submissions():
        title_matches = get_matching_modules_from_string(submission.title)
        body_matches = get_matching_modules_from_string(submission.selftext)
        matches = title_matches | body_matches
        if matches:
            submission_handler(submission, matches)
