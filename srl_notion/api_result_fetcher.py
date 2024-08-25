from typing import Optional, List, Dict, Generator, Any, Tuple
from collections import defaultdict, deque

import requests
from pydantic import HttpUrl


class ResultFetcher:

    GET_CHILDREN_URL = "https://api.notion.com/v1/blocks/{}/children"  # Fill with page id
    GET_PAGE_INFO = "https://api.notion.com/v1/pages/{}"  # Fill with page id

    PAGE_COL_NAME = "Pages"

    """ 
    Fetch the results of the raw json response (from NotionAPIConnector)
    """

    def __init__(self, raw_response: dict, headers: dict):
        self.raw_response = raw_response
        self.headers = headers

    @staticmethod
    def create_initial_dict(raw_response: Dict[str, Any]) -> Dict[str, str]:
        return {
            page["properties"]["Pages"]["title"][0]["plain_text"]: page["id"]
            for page in raw_response["results"]
        }

    @staticmethod
    def get_response_results(response_json: dict) -> list:
        return response_json.get("results", [])

    @staticmethod
    def fetch_url(headers: dict, url: HttpUrl) -> Optional[dict]:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    @staticmethod
    def fetch_children_from_page(id_: str, headers: dict) -> Optional[List[Dict]]:
        url = ResultFetcher.GET_CHILDREN_URL.format(id_)
        return ResultFetcher.get_response_results(
            ResultFetcher.fetch_url(headers=headers, url=url)
        )

    @staticmethod
    def fetch_page_info(id_: str, headers: dict) -> Optional[dict]:
        url = ResultFetcher.GET_PAGE_INFO.format(id_)
        return ResultFetcher.fetch_url(headers=headers, url=url)

    @staticmethod
    def is_it_a_container_page(pages: List[Dict]) -> bool:
        """
        Take the result of the "fetch_children_from_page" method
        """
        return all(page["type"] == "child_page" for page in pages)

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
        Recursive method to iterate through all pages and subpages
        Note : If a page or a subpage is empty, she cannot be yield
        """
        children_results = self.fetch_children_from_page(page_id, self.headers)

        # Check if the current page is not a container page (doesn't contain only subpages)
        if not ResultFetcher.is_it_a_container_page(pages=children_results):
            page_infos: dict = ResultFetcher.fetch_page_info(
                id_=page_id, headers=self.headers
            )
            page_url: HttpUrl = page_infos["url"]
            page_title: str = ResultFetcher.get_page_title(
                page_info_response=page_infos
            )

            yield subject_name, {page_title: page_url}

        # Iterate through the blocks in the children results
        for block in children_results:

            if block.get("type") == "child_page":
                subpage_id = block["id"]

                # Recursive call to explore subpages
                yield from self.fetch_all_pages(
                    page_id=subpage_id, subject_name=subject_name
                )

    def iterative_fetching(self) -> Generator[Tuple[str, Dict[str, HttpUrl]], None, None]:
        initial_dict = self.create_initial_dict(raw_response=self.raw_response)

        for main_page_name, main_page_id in initial_dict.items():

            # Start fetching from the main pages
            yield from self.fetch_all_pages(
                page_id=main_page_id, subject_name=main_page_name
            )

    @staticmethod
    def structure_gen_results(gen:Generator) -> List[Tuple[Dict[str, str]]]:
        return [res for res in gen]

    @staticmethod
    def prepare_output(fetcher_results:List[Tuple[Dict[str, str]]]) -> defaultdict[str, deque]:
        
        defdict_deque = defaultdict(deque)
        
        subject:str
        dict_page:Dict[str, HttpUrl]
        for subject, dict_page in fetcher_results:
            defdict_deque[subject].append(dict_page)
            
        return defdict_deque

    def main(self) -> defaultdict[str, deque]:
        gen = self.iterative_fetching()
        fetcher_results:List[Tuple[Dict[str, str]]] = ResultFetcher.structure_gen_results(gen=gen)
        return ResultFetcher.prepare_output(fetcher_results=fetcher_results)
    