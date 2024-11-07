from typing import List

from aiohttp import ClientSession
from random import choice

import logging

class Searcher:
    def __init__(self, api_keys: List[str], engine_id: str):
        self._session: ClientSession = None
        self._logger = logging.getLogger()
        self._keys = api_keys
        self._engine_id = engine_id

    async def start_client(self):
        self._session = ClientSession()

    async def stop_client(self):
        await self._session.close()

    async def search(self, query: str, offset: int=0, num_results: int=10, lang: str="ru", timeout=10):
        try:
            resp = await self._session.get(
                url="https://www.googleapis.com/customsearch/v1",
                params={
                    "q": query,
                    "num": num_results,
                    "hl": lang,
                    "start": offset,
                    "key": choice(self._keys),
                    "cx": self._engine_id
                },
                timeout=timeout,
            )
            resp.raise_for_status()
        except TimeoutError:
            self._logger.info(f"Таймаут запрпоса \"{query}\", параметры: offset={offset}, num_results={num_results}, lang={lang}, timeout={timeout}")
            return None

        data = await resp.json()

        results = [(result["title"], result["link"]) for result in data["items"]]

        self._logger.info(f"Получил ответ на запрос \"{query}\", язык: {lang}, диапазон: {offset}-{offset+num_results}, статус: {resp.status}, всего результатов: {len(results)}")

        return results

