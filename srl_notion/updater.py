import pickle
import pathlib
from typing import Any
from collections import defaultdict, deque


class DictDequeueStructureUpdater:
    """
    Takes the data structure in memory, as well as the structured response
    (output of ResultFetcher)
    and return the structured with the same order and updated (with the new pages, and without the deleted ones)
    """

    def __init__(self, response_result_fetcher: defaultdict[str, deque]):
        self.response_result_fetcher = response_result_fetcher

    # Réfléchir à comment je vais tester qu'une page est présente, nouvelle, ou à été supprimé (probablement une approche à base de sets)

    @staticmethod
    def load_in_memory_data_structure(
        data_structure_path: pathlib.Path,
    ) -> defaultdict[str, deque]:
        pass

    @staticmethod
    def load_pickle(path_object: pathlib.Path) -> Any:
        with open(path_object, "rb", encoding="utf-8") as f:  # rb -> Read Binary
            return pickle.load(f)

    @staticmethod
    def save_pickle(object_: Any, path_to_save: pathlib.Path) -> None:
        with open(path_to_save, "wb", encoding="utf-8") as f:
            pickle.dump(object_, f)
