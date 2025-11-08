import concurrent.futures

import requests
import structlog

from ou_bot.common.database import db
from ou_bot.common.ou_module import OUModule
from ou_bot.common.config import DatabaseConfig
from ou_bot.module_scraper.config import CourseListScraperConfig, ThreadConfig
from ou_bot.module_scraper.data_parser import CourseListParser, ModulePageParser
from ou_bot.module_scraper.scraper import Scraper

logger = structlog.stdlib.get_logger(__name__)


def get_module_urls(modules_url: str) -> list[str]:
    module_url_template = (
        "https://enrolment.open.ac.uk/page-data/courses/qualifications/details/{module_code}/page-data.json"
    )

    response = requests.get(modules_url)
    json_data = response.json()

    module_codes = [item["courseCode"] for item in json_data["result"]["pageContext"]["moduleExternalData"]]

    module_urls = [module_url_template.format(module_code=code.lower()) for code in module_codes]

    return module_urls


def scrape_module_page(url: str):
    try:
        module_page_parser = ModulePageParser()
        module_page_parser.url = url
        return module_page_parser.parse()
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None  # or log the error and continue


def scrape_module_pages(urls: list[str], config: ThreadConfig):
    max_workers = config.max_workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(scrape_module_page, url) for url in urls]
        concurrent.futures.wait(futures)
        results = [future.result() for future in futures]
        results = [r for r in results if r is not None]  # Filter out failed scrapes
        return results


def write_data_to_db(session: db, data: list[OUModule]) -> None:
    with session as database:
        for module in data:
            database.upsert_ou_module(module)


def run():
    logger.info("Attempting to scrape OU Modules")
    scraper_config = CourseListScraperConfig()
    thread_config = ThreadConfig()
    database_config = DatabaseConfig()

    scraper = Scraper(config=scraper_config)
    course_list_parser = CourseListParser()
    database = db(config=database_config)

    urls = get_module_urls(scraper_config.url)
    module_data = scrape_module_pages(urls, thread_config)
    if module_data:
        logger.info("Module data scraped.", scraped_module_qty=len(module_data))
    write_data_to_db(database, module_data)
