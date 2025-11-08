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
        course_list = soup.find(class_="productList")

        if course_list is None:
            raise ValueError(
                "Could not find element with class 'productList' on the page. "
                "The OU website structure may have changed."
            )

        # Find all ou-link elements with href attributes
        ou_links = course_list.find_all("ou-link")
        urls = [tag.get("href") for tag in ou_links if tag.get("href")]

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

    def _get_module_credits(self, soup: BeautifulSoup) -> int:
        # Credits value is currently two nodes after the header.
        credits_header = soup.find(lambda t: t.name == "h3" and t.text.strip() == "Credits")
        credits_value = credits_header.next_sibling.next_sibling
        return int(credits_value.text.strip())

    def _get_module_study_level(self, soup: BeautifulSoup) -> int:
        study_level_caption = soup.find(lambda t: t.name == "caption" and t.text.strip() == "Level of Study")
        parent_table = study_level_caption.parent
        study_level = parent_table.find("td").text.strip()
        return int(study_level)

    def _get_next_start(self, soup: BeautifulSoup) -> datetime | None:
        start_date = soup.find(lambda t: _has_one_of_id(t, "start-date"))
        if not start_date:
            return None
        try:
            dt = datetime.strptime(start_date.text, "%d %b %Y")
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
            next_start=self._get_next_start(soup),
        )
