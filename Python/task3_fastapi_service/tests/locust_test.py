from locust import HttpUser, between, task
import random

sample_urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3"
]

class APIShortLink(HttpUser):
    host = "http://localhost:9999"
    wait_time = between(1, 5)

    @task(3)
    def shorten_link(self):
        url = random.choice(sample_urls)
        short_link = f"short-{random.randint(1000, 9999)}"
        
        with self.client.post(
            "/shorten_links/links/shorten",
            json={
                "url": url,
                "short_link": short_link
            },
            name="/shorten_links [POST]",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Status code: {response.status_code}")

    @task(1)
    def get_link(self):
        short_link = f"short-{random.randint(1000, 9999)}"
        self.client.get(
            f"/shorten_links/links?short_link={short_link}",
            name="/shorten_links [GET]"
        )