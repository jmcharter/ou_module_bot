from dataclasses import dataclass
from datetime import datetime

from bs4 import BeautifulSoup

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
        course_list = soup.find(class_="course-list")
        a_tags = course_list.find_all("a")
        urls = [tag.get("href") for tag in a_tags]
        return urls


class ModulePageParser(DataParser):
    """Parse the module page and return module data

    The current module page (2023-05-27) does not give class names or ids to many of the
    values, so they need to be found by navigating from related headers.
    """

    url: str

    def _get_module_code(self, soup: BeautifulSoup) -> str:
        return soup.find("div", class_="product-module-code-identifier").text.strip()

    def _get_module_title(self, soup: BeautifulSoup) -> str:
        return soup.find("h1", class_="product-award-title-identifier").text.strip()

    def _get_module_credits(self, soup: BeautifulSoup) -> str:
        # Credits value is currently two nodes after the header.
        credits_header = soup.find(lambda t: t.name == "h3" and t.text.strip() == "Credits")
        credits_value = credits_header.next_sibling.next_sibling
        return credits_value.text.strip()

    def _get_module_study_level(self, soup: BeautifulSoup) -> str:
        study_level_caption = soup.find(lambda t: t.name == "caption" and t.text.strip() == "Level of Study")
        parent_table = study_level_caption.parent
        study_level = parent_table.find("td").text.strip()
        return study_level

    def _get_related_qualifications(self, soup: BeautifulSoup) -> list[str]:
        qual_list = soup.find("div", id="qual-list")
        if not qual_list:
            return []
        return [tag.text.strip() for tag in qual_list if tag.text.strip()]

    def _get_course_work_includes(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find("h3", string="Course work includes:").parent.parent.find_all("dd")
        if not items:
            return []
        items = items[1:]  # Remove first as it is just the subtitle
        return [item.text.strip() for item in items]

    def _get_next_start(self, soup: BeautifulSoup) -> datetime:
        start_date = soup.find(lambda t: t.get("id") and t.get("id").startswith("start-date")).text
        dt = datetime.strptime(start_date, "%d %b %Y")
        return dt

    def _get_next_end(self, soup: BeautifulSoup) -> datetime:
        end_date = soup.find(lambda t: t.get("id") and t.get("id").startswith("end-date")).text
        try:
            dt = datetime.strptime(end_date, "%b %Y")
        except ValueError:
            return None
        return dt

    def parse(self) -> OUModule:
        soup = self._get_soup()
        return OUModule(
            module_code=self._get_module_code(soup),
            module_title=self._get_module_title(soup),
            url=self.url,
            credits=self._get_module_credits(soup),
            ou_study_level=self._get_module_study_level(soup),
            related_qualifications=self._get_related_qualifications(soup),
            course_work_includes=self._get_course_work_includes(soup),
            next_start=self._get_next_start(soup),
            next_end=self._get_next_end(soup),
        )
