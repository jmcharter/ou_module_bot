import re
import time
from collections.abc import Callable

from cachetools.func import ttl_cache
from praw import Reddit, models
from praw.models.reddit.subreddit import SubredditStream
from prawcore.exceptions import RequestException, ServerError
import structlog

from ou_bot.common.database import ModuleRepository

logger = structlog.stdlib.get_logger(__name__)

type ModuleCode = str
type ModuleCodeSet = set[ModuleCode]

MODULES_TTL = 24 * 60 * 60  # 24 Hours


@ttl_cache(ttl=MODULES_TTL)
def get_tma_module_codes() -> list[str]:
    return ModuleRepository().get_all_codes()


def match_found(target: str, module: str) -> bool:
    return module.upper() in target.upper()


def get_matching_modules_from_string(target: str) -> set[str]:
    modules = get_tma_module_codes()
    return set(module for module in modules if match_found(target, module))


def scan_submissions(sub_name: str, reddit: Reddit, submission_handler: Callable[[models.Submission, set[str]], None]):
    subreddit = reddit.subreddit(sub_name)
    while True:
        try:
            for submission in subreddit.stream.submissions(skip_existing=True):
                title_matches = get_matching_modules_from_string(submission.title)
                body_matches = get_matching_modules_from_string(submission.selftext)
                matches = title_matches | body_matches
                if matches:
                    submission_handler(submission, matches)
        except (ServerError, RequestException) as e:
            logger.error("Submission stream error, restarting in 60s", error=str(e))
            time.sleep(60)
        except Exception as e:
            logger.error(
                "Unexpected submission stream error, restarting in 60s", error=str(e), error_type=type(e).__name__
            )
            time.sleep(60)


def get_called_modules(comment: str, modules: list[str]) -> ModuleCodeSet:
    comment = comment.upper().replace("\\", "")
    pattern = r"\[\[\s*(" + "|".join(re.escape(module) for module in modules) + r")\s*\]\]"
    matches = re.findall(pattern, comment)
    return set(matches)


def scan_comments(sub_name: str, reddit: Reddit, comment_handler: Callable[[models.Comment, ModuleCodeSet], None]):
    subreddit = reddit.subreddit(sub_name)
    comment_stream: SubredditStream = subreddit.stream
    while True:
        try:
            for comment in comment_stream.comments(skip_existing=True):
                modules = get_tma_module_codes()
                called_modules = get_called_modules(comment.body, modules)
                if called_modules:
                    comment_handler(comment, called_modules)
        except (ServerError, RequestException) as e:
            logger.error("Comment stream error, restarting in 60s", error=str(e))
            time.sleep(60)
        except Exception as e:
            logger.error(
                "Unexpected comment stream error, restarting in 60s", error=str(e), error_type=type(e).__name__
            )
            time.sleep(60)
