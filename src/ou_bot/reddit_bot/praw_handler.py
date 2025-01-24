import praw

from ou_bot.reddit_bot.config import PRAWConfig


def get_reddit_instance():
    config = PRAWConfig()
    reddit = praw.Reddit(
        client_id=config.client_id,
        client_secret=config.client_secret,
        password=config.password,
        user_agent=config.user_agent,
        username=config.username,
    )
    return reddit
