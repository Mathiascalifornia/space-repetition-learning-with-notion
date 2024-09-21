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

        self.count_dict: dict[str, int] = (
            InterfaceUser.create_if_needed_and_return_count_dict(
                updated_data_structure=self.updated_data_structure,
                path_pickle_dict=InterfaceUser.PATH_DICT_COUNT,
            )
        )

        atexit.register(
            self._save_data_structure_at_exit
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
                object_=self.count_dict, path_to_save=InterfaceUser.PATH_DICT_COUNT
            )

    def get_available_subjects(self) -> str:
        filtered_count_dict = {
            key: val
            for key, val in self.count_dict
            if key not in self.deleted_from_session_subjects
        }

        return " - ".join(list(filtered_count_dict.keys()))

    def propose_a_page(self, key_: str):

        to_propose: dict = self.data_structure_with_methods.get_last_element_of_deque(
            key=key_
        )
        subject = tuple(to_propose.keys())[0]

        propal_input = input(InterfaceUser.PROPAL_STRING.format(subject))

        if propal_input.strip().upper() == "N":
            self.data_structure_with_methods.randomly_resinsert_last_element(
                key_=subject
            )
            self.propose_a_page()  # Recursive call
        else:
            print(InterfaceUser.ACCEPTANCE_STRING.format(to_propose[subject]))
            self.data_structure_with_methods.shift_last_to_first(key_=key_)
            self.count_dict[key_] += 1

    def case_0_full_scope(self):

        random_key: str = self.data_structure_with_methods.get_random_key()
        while random_key in self.deleted_from_session_subjects:
            random_key: str = self.data_structure_with_methods.get_random_key()

        self.propose_a_page(key_=random_key)

    def case_1_shuffle_a_subject(self):

        input_shuffle = input(
            "Type the name of the subject you want to shuffle."
        ).strip()

        while input_shuffle not in self.count_dict:
            input_shuffle = input(
                f"This is not right. The subject has to be in the following list of subjects ; {self.get_available_subjects()}.\n"
            )

        self.data_structure_with_methods.random_shuffle(key_=input_shuffle)
        print("Shuffle done !")

    def case_2_delete_a_subject(self):

        input_deletion = input(
            "Type the name of the subject you want to delete from this session : "
        ).strip()
        while input_deletion not in self.count_dict:
            input_deletion = input(
                f"Unknowed subject. Available subject are ; {self.get_available_subjects()}"
            )

        if len(self.deleted_from_session_subjects) == len(self.count_dict):
            print(
                "You cannot delete every subject ! Reload the session or quit the program."
            )

        else:
            self.deleted_from_session_subjects.add(input_deletion)
            print(f"Subject : '{input_deletion}' removed from the current session")

    def case_3_reload_the_whole_scope(self):

        self.deleted_from_session_subjects = {}
        print(
            f"The session have been reloaded ! Now you can choose between all those subjects :\n {self.get_available_subjects()}"
        )

    def case_all_subjects_from_current_scope(self):
        updated_mapping_dict: dict = InterfaceUser.get_updated_version_of_mapping_dict(
            mapping_dict=self.mapping_dict,
            deleted_from_session_subjects=self.deleted_from_session_subjects,
        )
        updated_mapping_dict_str: str = InterfaceUser.get_updated_mapping_dict_str(
            updated_mapping_dict
        )

        input_subject = input(
            f"Choose the number related to a subject from the following list ; {updated_mapping_dict_str}"
        )

        while input_subject not in updated_mapping_dict:
            input_subject = input(
                f"Wrong input ; choose from this list :\n {updated_mapping_dict_str}"
            )

        self.propose_a_page(key_=self.updated_data_structure[input_subject])

    def main(self):

        menu = InterfaceUser.create_menu(
            updated_data_structure=self.updated_data_structure,
            count_dict=self.count_dict,
        )

        self.mapping_dict = InterfaceUser.create_mapping_user_choices(menu=menu)

        all_possible_choices = tuple(self.mapping_dict.keys())

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
                    self.case_2_delete_a_subject()

                case "3":
                    self.case_3_reload_the_whole_scope()

                case _:
                    self.case_all_subjects_from_current_scope()

            print("\n--------------------------------------------------\n")

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

    @staticmethod
    def get_updated_version_of_mapping_dict(
        mapping_dict: dict, deleted_from_session_subjects: set
    ) -> dict:
        return {
            key_: value
            for key_, value in mapping_dict.items()
            if key_ not in deleted_from_session_subjects
        }

    @staticmethod
    def get_updated_mapping_dict_str(updated_mapping_dict: dict) -> str:

        return "\n".join(
            [f"{key_} : {value} |" for key_, value in updated_mapping_dict.items()]
        )
