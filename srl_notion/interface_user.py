from collections import defaultdict, deque
import pathlib
import re

import utils


class InterfaceUser:
    """
    Bridge between the user and the data structure
    Take the up to date data structure, modify it as the user interact with it
    """

    BASE_MENU = "{}) All subjects\n{}) Shuffle the order for the current scope\n{}) Delete a subject from this session\n{}) Back to the default scope\n"
    BUILT_IN_OPTIONS = [
        base_option.replace("{}) ", "")
        for base_option in BASE_MENU.split("\n")
        if base_option
    ]

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

        mapping_choices = InterfaceUser.create_mapping_user_choices(menu=menu)

        all_possible_choices = tuple(mapping_choices.keys())

        while True:

            user_input = input(menu).strip()

            match user_input:

                case user_input if user_input not in all_possible_choices:
                    print(
                        f"You have to enter a single number in the range {all_possible_choices}"
                    )

                # Those will be the built in mapping logics
                case "0":
                    pass  # Random choice

                case "1":
                    pass

                case "2":
                    pass

                case "3":
                    pass

                # Then, it's a subset chosen and we have to filter based on that
                case _:
                    pass

        # return mapping_choices

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

    @staticmethod
    def create_mapping_user_choices(menu: str) -> dict:
        pattern = "^(.*?)(\(last seen ; )"

        splitted_menu = menu.split("\n")

        to_populate_dict = {}
        for possible_choice in splitted_menu:

            to_add_dict_key = possible_choice[0]
            to_add_dict_value = possible_choice[2:].strip()

            if to_add_dict_value not in InterfaceUser.BUILT_IN_OPTIONS:
                to_add_dict_value = re.findall(
                    pattern=pattern, string=to_add_dict_value
                )[0][0].strip()

            to_populate_dict[to_add_dict_key] = to_add_dict_value

        return to_populate_dict
