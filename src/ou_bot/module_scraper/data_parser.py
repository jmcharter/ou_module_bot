import re
from dataclasses import dataclass
from datetime import datetime

from bs4 import BeautifulSoup, Tag

from ou_bot.common.ou_module import OUModule


@dataclass
class DataParser:
    data: str = ""

    def _get_soup(self):
        return BeautifulSoup(self.data, "html.parser")

    def set_data(self, data: str) -> None:
        self.data = data

    def parse(self):
        raise NotImplementedError


class CourseListParser(DataParser):
    def parse(self) -> list[str]:
        soup = self._get_soup()
        course_lists = soup.find_all(class_="productList")

        if not course_lists:
            raise ValueError(
                "Could not find element with class 'productList' on the page. "
                "The OU website structure may have changed."
            )

        urls = []
        for course_list in course_lists:
            ou_links = course_list.find_all("ou-link")
            urls.extend([tag.get("href") for tag in ou_links if tag.get("href")])

        if not urls:
            raise ValueError(
                "No module URLs found in the productList. "
                "The OU website structure may have changed."
            )

        return urls


def _has_one_of_id(t: Tag, search_id: str) -> bool:
    match t.get("id"):
        case str(found_id) if found_id.startswith(search_id):
            return True
        case _:
            return False


@dataclass
class ModulePageParser(DataParser):
    url: str = ""

    def _get_module_code(self, soup: BeautifulSoup) -> str:
        canonical = soup.find("link", rel="canonical")
        if canonical and canonical.get("href"):
            return canonical.get("href").split("/")[-1].upper()
        return ""

    def _get_module_title(self, soup: BeautifulSoup) -> str:
        title_heading = soup.find("ou-heading", level="h1")
        if title_heading and title_heading.get("text"):
            return title_heading.get("text")
        return ""

    def _get_module_credits(self, soup: BeautifulSoup) -> int:
        credits_elem = soup.find("div", class_="injected-shadow-data", attrs={"data-title": "Credits"})
        if credits_elem:
            value = credits_elem.get("data-value", "")
            if value.isdigit():
                return int(value)
        return 0

    def _get_module_study_level(self, soup: BeautifulSoup) -> int:
        title_heading = soup.find("ou-heading", level="h1")
        if title_heading and title_heading.get("text"):
            title = title_heading.get("text")
            if "Access" in title:
                return 0

        level_elem = soup.find("div", class_="injected-shadow-data", attrs={"data-title": "Level"})
        if level_elem:
            value = level_elem.get("data-value", "")
            match = re.search(r"OU level:\s*(\d+)", value)
            if match:
                return int(match.group(1))

        for text in soup.find_all(string=lambda t: t and "OU level" in str(t)):
            match = re.search(r"OU level (\d+)", str(text))
            if match:
                return int(match.group(1))
        return 0

    def _get_next_start(self, soup: BeautifulSoup) -> datetime | None:
        table = soup.find("table")
        if not table:
            return None

        rows = table.find_all("tr")
        if len(rows) < 2:
            return None

        headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]
        cells = [td.get_text(strip=True) for td in rows[1].find_all("td")]

        if "Start" in headers and len(headers) == len(cells):
            start_idx = headers.index("Start")
            start_text = cells[start_idx]
            try:
                return datetime.strptime(start_text, "%d %b %Y")
            except ValueError:
                return None
        return None

    def parse(self) -> OUModule:
        soup = self._get_soup()
        return OUModule(
            module_code=self._get_module_code(soup),
            module_title=self._get_module_title(soup),
            url=self.url,
            credits=self._get_module_credits(soup),
            ou_study_level=self._get_module_study_level(soup),
            next_start=self._get_next_start(soup),
        )
