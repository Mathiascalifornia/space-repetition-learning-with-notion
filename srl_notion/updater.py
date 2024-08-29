import pickle
import pathlib
from typing import Any
from collections import defaultdict, deque

from pydantic import HttpUrl


class DictDequeueStructureUpdater:
    """
    Takes the data structure in memory, as well as the structured response
    (output of ResultFetcher)
    and return the structured with the same order and updated (with the new pages, and without the deleted ones)
    """

    PATH_DATA_STRUCTURE = pathlib.Path.cwd() / "data_structure.pkl"

    def __init__(self, response_result_fetcher: defaultdict[str, deque]):

        self.response_result_fetcher = response_result_fetcher
        self.saved_data_structure: defaultdict[str, deque] = (
            DictDequeueStructureUpdater._load_in_memory_data_structure()
        )

        self.converted_saved_data_structure: set[tuple] = (
            DictDequeueStructureUpdater._convert_data_structure_to_sets_of_tuple(
                data_structure=self.saved_data_structure
            )
        )
        self.converted_response_result_fetcher: set[tuple] = (
            DictDequeueStructureUpdater._convert_data_structure_to_sets_of_tuple(
                data_structure=self.response_result_fetcher
            )
        )

    # Idée de timeline ;
    # On crée des sets avec des tuples de trois éléments ; subject, nom de la page, clef
    # On fait ça pour les deux data structures (res fetcher et celle en mémoire)
    # Si une page est à rajouter ou supprimer, ce sera simple d'accès grâce au premier élément
    # On update la structure en mémoire, pas le résultat de res fetcher

    def update_and_save(self) -> defaultdict[str, deque]:

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

        DictDequeueStructureUpdater.save_pickle(
            object_=self.saved_data_structure,
            path_to_save=DictDequeueStructureUpdater.PATH_DATA_STRUCTURE,
        )

        return self.saved_data_structure

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

    # 1er test ; Une page supprimée
    # 2 ème test ; Une page ajoutée

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

                if url == saved_data_structure[subject][page_name]:
                    del saved_data_structure[subject][page_name]

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
    def _load_in_memory_data_structure(
        path_data_structure=pathlib.Path.cwd() / "data_structure.pkl",
    ) -> defaultdict[str, deque]:
        return DictDequeueStructureUpdater.load_pickle(path_object=path_data_structure)

    @staticmethod
    def load_pickle(path_object: pathlib.Path) -> Any:
        with open(path_object, "rb") as f:  # rb -> Read Binary
            return pickle.load(f)

    @staticmethod
    def save_pickle(object_: Any, path_to_save: pathlib.Path) -> None:
        with open(path_to_save, "wb") as f:
            pickle.dump(object_, f)
