import requests

from ou_bot.common.ou_module import OUModule


class ModulePageParser:
    """Parse the module page JSON data and return module data"""

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
            url=module_data["courseURL"].lower() if module_data["courseURL"] else "",
            credits=int(module_data["CreditPoints"]),
            ou_study_level=module_data["OUCourseLevel"],
            next_start=module_data["NextStartDate"],
        )
