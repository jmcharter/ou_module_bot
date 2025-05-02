#!/bin/bash
set -e

if [ "$1" = "bots" ]; then
    echo "Starting submission_bot and comment_bot..."
    poetry run submission_bot &
    poetry run comment_bot &
    # Keep container running
    tail -f /dev/null
elif [ "$1" = "scraper" ]; then
    echo "Running module_scraper..."
    poetry run module_scraper
elif [ "$1" = "scraper-loop" ]; then
    while true; do
        echo "Running module_scraper..."
        poetry run module_scraper
        echo "Sleeping for 1 week..."
        sleep 604800  # 7 days in seconds
    done
fi

exec "$@"
