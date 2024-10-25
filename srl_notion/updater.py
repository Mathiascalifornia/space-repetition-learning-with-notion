import datetime
import pathlib
from collections import defaultdict, deque


import utils


class DictDequeueStructureUpdater:
    """
    Takes the data structure in memory, as well as the structured response
    (output of ResultFetcher)
    and return the structured with the same order and updated (with the new pages, and without the deleted ones)
    """

    PATH_DATA_STRUCTURE = (
        pathlib.Path(__file__).resolve().parent / "data" / "data_structure.pkl"
    )

    def __init__(self, response_result_fetcher: defaultdict[str, deque]):

        print(
            f"In: {self.__class__.__name__} since {datetime.datetime.now().strftime('%H:%M:%S')}"
        )

        self.response_result_fetcher = response_result_fetcher

        try:
            self.saved_data_structure: defaultdict[str, deque] = (
                DictDequeueStructureUpdater._load_in_memory_data_structure(
                    path_data_structure=DictDequeueStructureUpdater.PATH_DATA_STRUCTURE
                )
            )

            self.converted_saved_data_structure: set[tuple] = (
                DictDequeueStructureUpdater._convert_data_structure_to_sets_of_tuple(
                    data_structure=self.saved_data_structure
                )
            )

        except FileNotFoundError:
            self.saved_data_structure = None
            self.converted_saved_data_structure = None
            print("No data structure in memory")

        self.converted_response_result_fetcher: set[tuple] = (
            DictDequeueStructureUpdater._convert_data_structure_to_sets_of_tuple(
                data_structure=self.response_result_fetcher
            )
        )

    @staticmethod
    def delete_empty_keys(
        data_structure: defaultdict[str, deque]
    ) -> defaultdict[str, deque]:
        keys_to_remove = [
            key for key, val in data_structure.items() if val == deque([])
        ]

        for key in keys_to_remove:
            del data_structure[key]

        return data_structure

    def update_and_save(self) -> defaultdict[str, deque]:

        if not self.saved_data_structure:
            return DictDequeueStructureUpdater.delete_empty_keys(
                self.response_result_fetcher
            )

        self.saved_data_structure: defaultdict[str, deque] = (
            DictDequeueStructureUpdater.remove_new_pages(
                converted_response_result_fetcher=self.converted_response_result_fetcher,
                converted_saved_data_structure=self.converted_saved_data_structure,
                saved_data_structure=self.saved_data_structure,
            )
        )

        self.saved_data_structure: defaultdict[str, deque] = (
            DictDequeueStructureUpdater.add_new_pages(
                converted_response_result_fetcher=self.converted_response_result_fetcher,
                converted_saved_data_structure=self.converted_saved_data_structure,
                saved_data_structure=self.saved_data_structure,
            )
        )

        utils.save_pickle(
            object_=self.saved_data_structure,
            path_to_save=DictDequeueStructureUpdater.PATH_DATA_STRUCTURE,
        )

        return DictDequeueStructureUpdater.delete_empty_keys(self.saved_data_structure)

    @staticmethod
    def _convert_data_structure_to_sets_of_tuple(
        data_structure: defaultdict[str, deque]
    ) -> set[tuple]:

        return {
            (subject, page_name, url)
            for subject in data_structure
            for dict_ in data_structure[subject]
            for page_name, url in dict_.items()
        }

    @staticmethod
    def remove_new_pages(
        converted_saved_data_structure: set[tuple],
        converted_response_result_fetcher: set[tuple],
        saved_data_structure: defaultdict[str, deque],
    ) -> defaultdict[str, deque]:

        tuple_: tuple[str, str, str]
        for tuple_ in converted_saved_data_structure:

            if (
                tuple_ not in converted_response_result_fetcher
            ):  # Then it has been deleted

                subject = tuple_[0]
                page_name = tuple_[1]
                url = tuple_[2]

                dict_: dict
                for dict_ in list(
                    saved_data_structure[subject]
                ):  # Turn the structure to a list, to make it a copy of the object and not the actual object (in order to be able to use the remove method during iteration)

                    res_key = dict_.get(page_name, [])

                    if res_key:

                        if (
                            url == res_key
                        ):  # We want to be sure that, even if two page names are similar the URL is different
                            saved_data_structure[subject].remove(dict_)

        return saved_data_structure

    @staticmethod
    def add_new_pages(
        converted_saved_data_structure: set[tuple],
        converted_response_result_fetcher: set[tuple],
        saved_data_structure: defaultdict[str, deque],
    ) -> defaultdict[str, deque]:

        tuple_: tuple[str, str, str]
        for tuple_ in converted_response_result_fetcher:

            if tuple_ not in converted_saved_data_structure:  # Then it has been deleted

                subject = tuple_[0]
                page_name = tuple_[1]
                url = tuple_[2]

                saved_data_structure[subject].appendleft({page_name: url})

        return saved_data_structure

    @staticmethod
    def _load_in_memory_data_structure(path_data_structure) -> defaultdict[str, deque]:
        return utils.load_pickle(path_object=path_data_structure)
