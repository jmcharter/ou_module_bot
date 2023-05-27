from ou_bot.module_scraper.config import DatabaseConfig, ScraperConfig, CourseListScraperConfig, ThreadConfig
from ou_bot.module_scraper.data_parser import DataParser, CourseListParser, ModulePageParser
from ou_bot.module_scraper.scraper import Scraper
from ou_bot.module_scraper.database import db

import os
import concurrent.futures

from ou_bot.ou_module import OUModule


def get_module_urls(scraper: Scraper, parser: DataParser) -> list[str]:
    data = scraper.scrape_text()
    parser.set_data(data)
    return parser.parse()


def scrape_module_page(url: str):
    config = ScraperConfig(url=url)
    scraper = Scraper(config=config)
    data = scraper.scrape_text()
    module_page_parser = ModulePageParser()
    module_page_parser.set_data(data)
    module_page_parser.url = url
    return module_page_parser.parse()


def scrape_module_pages(urls: list[str], config: ThreadConfig):
    max_workers = config.max_workers
    base_url = os.environ.get("OU_BASE_URL") or "https://www.open.ac.uk"
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(scrape_module_page, base_url + url) for url in urls]
        concurrent.futures.wait(futures)
        results = [future.result() for future in futures]
        return results


def write_data_to_db(session: db, data: list[OUModule]) -> None:
    with session as database:
        for module in data:
            database.add_ou_module(module)


def run():
    scraper_config = CourseListScraperConfig()
    thread_config = ThreadConfig()
    database_config = DatabaseConfig()

    scraper = Scraper(config=scraper_config)
    course_list_parser = CourseListParser()
    database = db(config=database_config)

    urls = get_module_urls(scraper, course_list_parser)
    module_data = scrape_module_pages(urls, thread_config)
    write_data_to_db(database, module_data)
