from dataclasses import dataclass
import time

from playwright.sync_api import sync_playwright

from ou_bot.module_scraper.config import ScraperConfig


@dataclass
class Scraper:
    config: ScraperConfig

    def scrape_text(self) -> str:
        url = self.config.url

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                ]
            )
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
            )
            page = context.new_page()

            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            page.goto(url, wait_until='domcontentloaded')

            try:
                page.wait_for_selector('ou-block-list-item', timeout=10000)

                # Extract shadow DOM data and inject into HTML
                page.evaluate('''() => {
                    const blockList = document.querySelector('ou-block-list');
                    if (blockList && blockList.shadowRoot) {
                        const items = blockList.shadowRoot.querySelectorAll('ou-block-list-item');
                        items.forEach(item => {
                            const title = item.getAttribute('title');
                            const value = item.textContent.trim();
                            const newElement = document.createElement('div');
                            newElement.className = 'injected-shadow-data';
                            newElement.setAttribute('data-title', title);
                            newElement.setAttribute('data-value', value);
                            newElement.textContent = value;
                            blockList.appendChild(newElement);
                        });
                    }
                }''')
            except:
                page.wait_for_timeout(5000)

            content = page.content()
            browser.close()

        return content
