# Headless scrape of new cryptopanic.com/news/bitcoin articles.

import time
from datetime import datetime, timezone

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


class CryptoPanicCollector:
    URL = "https://cryptopanic.com/news/bitcoin/"
    ARTICLE_SELECTOR = ".news-row-link"
    CONTAINER_SELECTOR = ".news-container"
    MAX_SCROLLS = 25

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def _driver(self) -> webdriver.Chrome:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        return webdriver.Chrome(options=options)

    @staticmethod
    def _timestamp(block) -> datetime:
        value = block.find_element(
            By.CSS_SELECTOR, ".news-cells .nc-date time"
        ).get_attribute("datetime")
        return datetime.strptime(
            value.split(" GMT")[0], "%a %b %d %Y %H:%M:%S"
        ).replace(tzinfo=timezone.utc)

    def _listing(self, driver, since: datetime) -> list[dict]:
        container = driver.find_element(By.CSS_SELECTOR, self.CONTAINER_SELECTOR)
        for _ in range(self.MAX_SCROLLS):
            blocks = driver.find_elements(By.CSS_SELECTOR, self.ARTICLE_SELECTOR)
            if blocks and self._timestamp(blocks[-1]) <= since:
                break
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", container
            )
            time.sleep(1)

        articles = []
        for block in driver.find_elements(By.CSS_SELECTOR, self.ARTICLE_SELECTOR):
            try:
                timestamp = self._timestamp(block)
                url = block.find_element(By.CSS_SELECTOR, ".nc-title").get_attribute(
                    "href"
                )
                if timestamp > since and url and not url.endswith("/news/bitcoin/"):
                    articles.append({"timestamp": timestamp, "url": url})
            except (NoSuchElementException, ValueError):
                continue
        return articles

    def _article(self, driver, metadata: dict) -> dict | None:
        try:
            driver.get(metadata["url"])
            body = WebDriverWait(driver, self.timeout).until(
                expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, ".description-body")
                )
            )
            if "<br>" in body.get_attribute("innerHTML"):
                return None
            title = driver.title.removesuffix(" - CryptoPanic").strip()
            summary = body.text.strip()
            if not title or not summary:
                return None
            return {**metadata, "title": title, "summary": summary}
        except (TimeoutException, WebDriverException):
            return None

    def collect_since(self, since: datetime) -> list[dict]:
        driver = self._driver()
        driver.set_page_load_timeout(self.timeout)
        try:
            driver.get(self.URL)
            WebDriverWait(driver, self.timeout).until(
                expected_conditions.presence_of_element_located((By.TAG_NAME, "body"))
            )
            metadata = self._listing(driver, since)
            return [
                article
                for item in metadata
                if (article := self._article(driver, item)) is not None
            ]
        finally:
            driver.quit()
