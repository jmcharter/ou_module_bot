from typing import Optional
from pydantic import BaseSettings, Field


class PRAWConfig(BaseSettings):
    client_id: str = Field(..., env="CLIENT_ID", description="Reddit Client ID")
    client_secret: str = Field(..., env="CLIENT_SECRET", description="Reddit Client Secret")
    user_agent: str = Field(..., env="REDDIT_USER_AGENT", description="Reddit User Agent")
    username: str = Field(..., env="REDDIT_USERNAME", description="Reddit Bot Account's Username")
    password: str = Field(..., env="REDDIT_PASSWORD", description="Reddit Bot Account's Password")


class MakoConfig(BaseSettings):
    template_dir: str = Field(..., env="MAKO_TEMPLATE_DIR", description="The directory where make templates are stored")
    module_dir: Optional[str] = Field(
        None, env="MAKO_MODULE_DIR", description="Directory to store and read generated module files"
    )
    output_encoding: str = Field(
        "utf-8", env="MAKO_OUTPUT_ENCODING", description="Encoding type for Mako output, e.g. utf-8"
    )


class AppConfig(BaseSettings):
    praw: PRAWConfig = Field(default_factory=lambda: PRAWConfig())
    mako: MakoConfig = Field(default_factory=lambda: MakoConfig())
    subreddit: str = Field(
        ..., env="SUBREDDIT", description="The subreddit the application will scan the posts of and respond to"
    )
    max_retry_attempts: int = Field(
        12, env="MAX_RETRY_ATTEMPTS", description="Maximum number of retry attempts for Reddit API calls (12 attempts = ~1 hour total retry time)"
    )
