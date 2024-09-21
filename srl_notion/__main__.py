from collections import deque, defaultdict

from api_connection import NotionAPIConnector
from api_result_fetcher import ResultFetcher
from updater import DictDequeueStructureUpdater
from interface_user import InterfaceUser


def main():

    connector = NotionAPIConnector()
    raw_response: dict = connector.main()
    headers = connector.headers

    fetcher = ResultFetcher(raw_response=raw_response, headers=headers)

    raw_res: defaultdict[str, deque] = fetcher.main()

    updater = DictDequeueStructureUpdater(response_result_fetcher=raw_res)

    up_to_date_data_structure: defaultdict[str, deque] = updater.update_and_save()

    InterfaceUser(up_to_date_data_structure).main()


if __name__ == "__main__":
    main()
