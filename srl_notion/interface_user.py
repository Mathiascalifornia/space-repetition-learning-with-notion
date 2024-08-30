from typing import Optional, List, Dict, Generator, Any, Tuple
from collections import defaultdict, deque
import pathlib

import requests
from pydantic import HttpUrl


import utils


class InterfaceUser:
    """
    Bridge between the user and the data structure
    Take the up to date data structure, modify it as the user interact with it
    """

    BASE_MENU = "{}) All subjects\n{}) Shuffle the order for the current scope\n{}) Delete a subject from this session\n{}) Back to the default scope\n"

    PATH_DICT_COUNT = pathlib.Path.cwd() / "data" / "count_dict_structure.pkl"

    def __init__(self, updated_data_structure: defaultdict[str, deque]):
        self.updated_data_structure = updated_data_structure

    def main(self):

        count_dict: dict[str, int] = InterfaceUser.update_or_create_count_dict(
            updated_data_structure=self.updated_data_structure,
            path_pickle_dict=InterfaceUser.PATH_DICT_COUNT,
        )
        menu = InterfaceUser.create_menu(
            updated_data_structure=self.updated_data_structure, count_dict=count_dict
        )

        ### Create the main loop ###

        return menu

    @staticmethod
    def update_or_create_count_dict(
        updated_data_structure: defaultdict[str, deque], path_pickle_dict: pathlib.Path
    ) -> dict[str, int]:
        """
        To keep track of the number of session that the user haven't read about a given subject
        """
        if not pathlib.Path.exists(path_pickle_dict):

            dict_to_save = {subject: 0 for subject in updated_data_structure}

            utils.save_pickle(
                object_=dict_to_save, path_to_save=InterfaceUser.PATH_DICT_COUNT
            )

            return dict_to_save

        else:
            saved_dict: dict = utils.load_pickle(
                path_object=InterfaceUser.PATH_DICT_COUNT
            )

            subject: str
            for subject in updated_data_structure:
                saved_dict.setdefault(subject, 0)

            return saved_dict

    @staticmethod
    def create_menu(
        updated_data_structure: defaultdict[str, deque], count_dict: dict[str, int]
    ) -> str:

        number_of_elements: int = len(InterfaceUser.BASE_MENU.split("\n")) + len(
            updated_data_structure
        )

        subjects_to_add_to_menu: str = "\n".join(
            [
                "{}) "
                + subject
                + f" (last seen ; {count_dict[subject]} session(s) ago)"
                for subject in updated_data_structure
            ]
        )

        final_menu: str = InterfaceUser.BASE_MENU + subjects_to_add_to_menu
        return final_menu.format(*list(range(number_of_elements)))
