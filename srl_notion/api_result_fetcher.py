import datetime
import time
from typing import Optional, List, Dict, Generator, Any, Tuple
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor

import requests
from pydantic import HttpUrl


class ResultFetcher:

    GET_CHILDREN_URL = (
        "https://api.notion.com/v1/blocks/{}/children"  # Fill with page id
    )
    GET_PAGE_INFO = "https://api.notion.com/v1/pages/{}"  # Fill with page id

    PAGE_COL_NAME = "Pages"
    MAX_WORKERS = 4
    REQUEST_TIMEOUT = 10
    RETRY_STATUS = {429, 500, 502, 503, 504}
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 0.5

    """
    Fetch the results of the raw json response (from NotionAPIConnector)
    """

    def __init__(self, raw_response: dict, headers: dict):
        print(
            f"In: {self.__class__.__name__} since {datetime.datetime.now().strftime('%H:%M:%S')}"
        )
        self.raw_response = raw_response
        self.headers = headers
        self.session = requests.Session()
        self.session.headers.update(headers)

    @staticmethod
    def create_initial_dict(raw_response: Dict[str, Any]) -> Dict[str, str]:
        return {
            page["properties"]["Pages"]["title"][0]["plain_text"]: page["id"]
            for page in raw_response["results"]
        }

    @staticmethod
    def get_response_results(response_json: dict) -> list:
        return response_json.get("results", [])

    def fetch_url(self, url: HttpUrl) -> Optional[dict]:
        for attempt in range(self.MAX_RETRIES):
            response = self.session.get(url, timeout=self.REQUEST_TIMEOUT)
            if response.status_code == 200:
                return response.json()

            if response.status_code not in self.RETRY_STATUS:
                response.raise_for_status()

            time.sleep(self.BACKOFF_FACTOR * (2 ** attempt))

        response.raise_for_status()

    def fetch_children_from_page(self, id_: str) -> Optional[List[Dict]]:
        url = ResultFetcher.GET_CHILDREN_URL.format(id_)
        page_json = self.fetch_url(url=url)
        return ResultFetcher.get_response_results(page_json or {})

    def fetch_page_info(self, id_: str) -> Optional[dict]:
        url = ResultFetcher.GET_PAGE_INFO.format(id_)
        return self.fetch_url(url=url)

    @staticmethod
    def is_it_a_container_page(pages: List[Dict]) -> bool:
        """
        Take the result of the "fetch_children_from_page" method
        """
        return bool(pages) and all(page["type"] == "child_page" for page in pages)

    @staticmethod
    def get_page_title(page_info_response: dict) -> str:
        return page_info_response["properties"].get("Pages", {}).get("title", [{}])[
            0
        ].get("plain_text", "") or page_info_response["properties"].get(
            "title", {}
        ).get(
            "title", [{}]
        )[
            0
        ].get(
            "plain_text", ""
        )

    def fetch_all_pages(
        self, page_id: str, subject_name: str
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Iterative method to traverse all pages and subpages.
        """
        queue = deque([page_id])

        while queue:
            batch = [queue.popleft() for _ in range(min(len(queue), self.MAX_WORKERS))]
            page_ids = batch

            with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
                children_results_list = list(
                    executor.map(self.fetch_children_from_page, page_ids)
                )

            leaf_page_ids = []
            for current_id, children_results in zip(page_ids, children_results_list):
                if not ResultFetcher.is_it_a_container_page(pages=children_results):
                    leaf_page_ids.append(current_id)

                for block in children_results:
                    if block.get("type") == "child_page":
                        queue.append(block["id"])

            if leaf_page_ids:
                with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
                    page_infos_list = list(executor.map(self.fetch_page_info, leaf_page_ids))

                for page_infos in page_infos_list:
                    page_url: HttpUrl = page_infos["url"]
                    page_title: str = ResultFetcher.get_page_title(
                        page_info_response=page_infos
                    )
                    yield subject_name, {page_title: page_url}

    def iterative_fetching(
        self,
    ) -> Generator[Tuple[str, Dict[str, HttpUrl]], None, None]:
        initial_dict = self.create_initial_dict(raw_response=self.raw_response)

        for main_page_name, main_page_id in initial_dict.items():
            yield from self.fetch_all_pages(
                page_id=main_page_id, subject_name=main_page_name
            )

    @staticmethod
    def structure_gen_results(gen: Generator) -> List[Tuple[Dict[str, str]]]:
        return [res for res in gen]

    @staticmethod
    def prepare_output(
        fetcher_results: List[Tuple[Dict[str, str]]]
    ) -> defaultdict[str, deque]:

        defdict_deque = defaultdict(deque)

        subject: str
        dict_page: Dict[str, HttpUrl]
        for subject, dict_page in fetcher_results:
            defdict_deque[subject].append(dict_page)

        return defdict_deque

    def main(self) -> defaultdict[str, deque]:
        gen = self.iterative_fetching()
        fetcher_results: List[Tuple[Dict[str, str]]] = (
            ResultFetcher.structure_gen_results(gen=gen)
        )
        return ResultFetcher.prepare_output(fetcher_results=fetcher_results)
