from dataclasses import dataclass
from datetime import datetime

from bs4 import BeautifulSoup, Tag
import requests

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
        course_url_template = (
            "https://enrolment.open.ac.uk/page-data/courses/qualifications/details/{module_code}/page-data.json"
        )
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
            raise ValueError("No module URLs found in the productList. " "The OU website structure may have changed.")

        return urls


def _has_one_of_id(t: Tag, search_id: str) -> bool:
    match t.get("id"):
        case str(found_id) if found_id.startswith(search_id):
            return True
        case _:
            return False


class ModulePageParser:
    """Parse the module page and return module data

    The current module page (2023-05-27) does not give class names or ids to many of the
    values, so they need to be found by navigating from related headers.
    """

    url: str

    def _get_json(self):
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()  # Raise an error for bad status codes
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from {self.url}: {e}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch {self.url}: {e}")

    def parse(self) -> OUModule:
        json_data = self._get_json()

        try:
            module_data = json_data["result"]["pageContext"]["moduleExternalData"]["data"]["allOuModuleType"]["edges"][
                0
            ]["node"]["CourseDetails"]
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Could not parse module data from {self.url}: {e}")

        return OUModule(
            module_code=module_data["courseCode"],
            module_title=module_data["courseTitle"],
            url=module_data["courseURL"],
            credits=int(module_data["CreditPoints"]),
            ou_study_level=module_data["OUCourseLevel"],
            next_start=module_data["NextStartDate"],
        )
