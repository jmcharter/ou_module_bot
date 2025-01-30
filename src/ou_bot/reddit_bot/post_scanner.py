import re
from typing import Callable, Optional

from cachetools.func import ttl_cache
from praw import models, Reddit
from praw.models.reddit.subreddit import SubredditStream

from ou_bot.common.config import DatabaseConfig
from ou_bot.common.database import db

MODULES_TTL = 24 * 60 * 60  # 24 Hours


@ttl_cache(ttl=MODULES_TTL)
def get_tma_modules() -> list[str]:
    database_config = DatabaseConfig()
    database = db(database_config)
    with database as session:
        module_codes = session.get_all_module_codes()
        return module_codes


def match_found(target: str, module: str) -> bool:
    return module.upper() in target.upper()


def get_matching_modules_from_string(target: str) -> set[str]:
    modules = get_tma_modules()
    return set(module for module in modules if match_found(target, module))


def scan_submissions(sub_name: str, reddit: Reddit, submission_handler: Callable[[models.Submission, set[str]], None]):
    subreddit = reddit.subreddit(sub_name)
    for submission in subreddit.stream.submissions(skip_existing=True):
        title_matches = get_matching_modules_from_string(submission.title)
        body_matches = get_matching_modules_from_string(submission.selftext)
        matches = title_matches | body_matches
        if matches:
            submission_handler(submission, matches)


def get_called_modules(comment: str, modules: list[str]) -> set[str]:
    pattern = r"\[\[(" + "|".join(re.escape(module) for module in modules) + r")\]\]"
    matches = re.findall(pattern, comment)
    return set(matches)


def scan_comments(sub_name: str, reddit: Reddit, comment_handler: Callable[[models.Comment, set[str]], None]):
    subreddit = reddit.subreddit(sub_name)
    comment_stream: SubredditStream = subreddit.stream
    for comment in comment_stream.comments(skip_existing=True):
        modules = get_tma_modules()
        called_modules = get_called_modules(comment.body, modules)
        if called_modules:
            comment_handler(comment, called_modules)
