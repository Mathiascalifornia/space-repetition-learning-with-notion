from collections import defaultdict, deque
import pathlib
import atexit
import re

import utils
from dict_deque import DictQueueStructure


# TODO 
# Remember to add the updated menu at strategic points
# Blow this class into two separate classes


class InterfaceUser:
    """
    Bridge between the user and the data structure
    Take the up to date data structure, modify it as the user interact with it
    """

    BASE_MENU = "{}) Get a page from the current scope\n{}) Shuffle the order for a subject\n{}) Delete a subject from this session\n{}) Back to the default scope\n"
    BUILT_IN_OPTIONS = [
        base_option.replace("{}) ", "")
        for base_option in BASE_MENU.split("\n")
        if base_option
    ]

    PATH_DATA_FOLDER = pathlib.Path.cwd() / "data"
    PATH_DATA_STRUCTURE = PATH_DATA_FOLDER / "data_structure.pkl"
    PATH_DICT_COUNT = PATH_DATA_FOLDER / "count_dict_structure.pkl"

    PROPAL_STRING = "Type 'N' if you don't want to see this page, any other keystroke otherwise : {} ?"
    ACCEPTANCE_STRING = "Happy learning ; {}"

    utils = utils

    def __init__(self, updated_data_structure: defaultdict[str, deque]):
        self.updated_data_structure = updated_data_structure
        self.deleted_from_session_subjects = set()

        atexit.register(
            self._save_data_structure_at_exit()
        )  # Save the data structure at exit

    def _save_data_structure_at_exit(self) -> None:
        if hasattr(self, "data_structure_with_methods"):
            InterfaceUser.utils.save_pickle(
                object_=self.data_structure_with_methods.data_structure,
                path_to_save=InterfaceUser.PATH_DATA_FOLDER,
            )

            print(
                f"Exiting the program. The up to date data structure has been saved in '{InterfaceUser.PATH_DATA_FOLDER}'."
            )

        if hasattr(self, "count_dict"):
            InterfaceUser.utils.save_pickle(
                object_=self.count_dict, 
                path_to_save=InterfaceUser.PATH_DICT_COUNT
            )

    def case_0_full_scope(self):

        random_key: str = self.data_structure_with_methods.get_random_key()
        while random_key in self.deleted_from_session_subjects:
            random_key: str = self.data_structure_with_methods.get_random_key()

        to_propose: dict = self.data_structure_with_methods.get_last_element_of_deque(
            key=random_key
        )
        subject = tuple(to_propose.keys())[0]

        propal_input = input(InterfaceUser.PROPAL_STRING.format(subject))

        if propal_input.strip().upper() == "N":
            self.data_structure_with_methods.randomly_resinsert_last_element(
                key_=subject
            )
            self.case_0_full_scope()  # Recursive call
        else:
            print(InterfaceUser.ACCEPTANCE_STRING.format(to_propose[subject]))
            self.data_structure_with_methods.shift_last_to_first(key_=random_key)
            self.count_dict[subject] += 1

    def case_1_shuffle_a_subject(self):
        
        input_shuffle = input("Type the name of the subject you want to shuffle.").strip()
        
        while input_shuffle not in self.count_dict:
            all_subject_to_display = ' - '.join(list(self.count_dict.keys()))
            input_shuffle = input(f"This is not right. The subject has to be in the following list of subjects ; {all_subject_to_display}.")
        
        self.data_structure_with_methods.random_shuffle(key_=input_shuffle)




    def main(self):

        self.count_dict: dict[str, int] = InterfaceUser.create_if_needed_and_return_count_dict(
            updated_data_structure=self.updated_data_structure,
            path_pickle_dict=InterfaceUser.PATH_DICT_COUNT,
        )
        menu = InterfaceUser.create_menu(
            updated_data_structure=self.updated_data_structure, count_dict=self.count_dict
        )

        mapping_choices = InterfaceUser.create_mapping_user_choices(menu=menu)

        all_possible_choices = tuple(mapping_choices.keys())

        self.data_structure_with_methods = DictQueueStructure(
            data_structure=self.updated_data_structure
        )

        while True:

            user_input = input(menu).strip()

            match user_input:

                case user_input if user_input not in all_possible_choices:
                    print(
                        f"You have to enter a single number in the range {all_possible_choices}"
                    )

                # Those will be the built in mapping logics
                case "0":
                    self.case_0_full_scope()


                case "1":
                    self.case_1_shuffle_a_subject()

                case "2":
                    # Faire en sorte que l'utilisateur ne supprime pas tout
                    pass

                case "3":
                    pass

                # Then, it's a subset chosen and we have to filter based on that
                case _:
                    pass

        # return mapping_choices

    @staticmethod
    def create_if_needed_and_return_count_dict(
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
