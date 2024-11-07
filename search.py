from aiohttp import ClientSession
from random_user_agent.user_agent import UserAgent
from bs4 import BeautifulSoup
from random import choice

software_names = ["firefox"]
operating_systems = ["windows", "linux"]

_user_agent_rotator = UserAgent(
    software_names=software_names,
    operating_systems=operating_systems
)

_magic_useragents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0'
]

class Searcher:
    def __init__(self):
        self._session: ClientSession = None

    async def start_client(self):
        self._session = ClientSession()

    async def stop_client(self):
        await self._session.close()

    async def search(self, query: str, offset: int=0, num_results: int=10, lang: str="ru"):
        resp = await self._session.get(
            url="https://www.google.com/search",
            headers={
                # "User-Agent": _user_agent_rotator.get_random_user_agent()
                "User-Agent": choice(_magic_useragents)
            },
            params={
                "q": query,
                "num": num_results,
                "hl": lang,
                "start": offset,
                "safe": "active",
            },
        )
        resp.raise_for_status()

        html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        result_block = soup.find_all("div", attrs={"class": "g"})
        results = []

        for result in result_block:
            link = result.find("a", href=True)
            title = result.find("h3")
            results.append((title.text, link["href"]))

        return results
