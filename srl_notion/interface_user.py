from collections import defaultdict, deque
import pathlib
import atexit
import re

import utils
from dict_deque import DictQueueStructure

# BUG
# Problème de logique dans les N session ago -> changer pour mettre une date à la place
# Le menu ne s'affiche pas dynamiquement (au fil des éléments supprimés) -> re-créer le menu dynamiquement via une fonction dans la boucle while en intégrant les éléments supprimés

# TODO
# Create the updated menu at the end of the loop
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

    PATH_DATA_FOLDER = pathlib.Path(__file__).resolve().parent / "data"
    PATH_DATA_STRUCTURE = PATH_DATA_FOLDER / "data_structure.pkl"
    PATH_DICT_COUNT = PATH_DATA_FOLDER / "count_dict_structure.pkl"

    PROPAL_STRING = "Type 'N' if you don't want to see this page, any other keystroke otherwise : {} "
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
                path_to_save=InterfaceUser.PATH_DATA_STRUCTURE,
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
            for key, val in self.count_dict.items()
            if key not in self.deleted_from_session_subjects
        }

        return " - ".join(list(filtered_count_dict.keys()))

    def propose_a_page(self, subject: str):

        try:
            to_propose: dict = self.data_structure_with_methods.get_last_element_of_deque(
                key=subject
            )
        except IndexError:
            return
        
        page_name = tuple(to_propose.keys())[0]

        propal_input = input(InterfaceUser.PROPAL_STRING.format(subject + " >> " + page_name))

        if propal_input.strip().upper() == "N":
            self.data_structure_with_methods.randomly_resinsert_last_element(
                key_=subject
            )
            self.propose_a_page(subject)  # Recursive call
        else:

            print("\n")
            print("-------------------------------------")
            print(InterfaceUser.ACCEPTANCE_STRING.format(to_propose[page_name]))
            print("-------------------------------------\n")
            self.data_structure_with_methods.shift_last_to_first(key_=subject)
            self.count_dict[subject] += 1

    def case_0_full_scope(self):

        random_key: str = self.data_structure_with_methods.get_random_key()

        while random_key in self.deleted_from_session_subjects:
            random_key: str = self.data_structure_with_methods.get_random_key()

        self.propose_a_page(subject=random_key)

    def case_1_shuffle_a_subject(self):

        input_shuffle = input(
            "\nType the number of the subject you want to shuffle ; "
        ).strip()

        updated_mapping_dict = InterfaceUser.get_updated_version_of_mapping_dict(mapping_dict=self.mapping_dict, 
                                                                                 deleted_from_session_subjects=self.deleted_from_session_subjects)
        
        while input_shuffle not in updated_mapping_dict:
            input_shuffle = input(
                f"This is not right. The subject has to be in the following list of subjects ; {self.get_available_subjects()}.\n"
            )

        self.data_structure_with_methods.random_shuffle(key_=updated_mapping_dict[input_shuffle])
        print("\n")
        print('--------------------------------------------------')
        print("Shuffle done !\n")
        print('--------------------------------------------------')

    def case_2_delete_a_subject(self):

        input_deletion = input(
            "Type the number of the subject you want to delete from this session : "
        ).strip()

        updated_mapping_dict = InterfaceUser.get_updated_version_of_mapping_dict(mapping_dict=self.mapping_dict, 
                                                                                 deleted_from_session_subjects=self.deleted_from_session_subjects)

        while input_deletion not in updated_mapping_dict:
            input_deletion = input(
                f"Unknowed subject. Available subject are ; {self.get_available_subjects()}"
            )

        if len(self.deleted_from_session_subjects) == len(self.count_dict):
            print(
                "You cannot delete every subject ! Reload the session or quit the program."
            )

        else:
            subject = updated_mapping_dict[input_deletion]
            self.deleted_from_session_subjects.add(input_deletion)
            print(f"\nSubject : '{subject}' removed from the current session\n")
            print("--------------------------------------------------")

    def case_3_reload_the_whole_scope(self):

        self.deleted_from_session_subjects = set()
        print(
            f"The session have been reloaded ! Now you can choose between all those subjects :\n {self.get_available_subjects()}"
        )

    def case_all_subjects_from_current_scope(self, input_user:str):
        updated_mapping_dict: dict = InterfaceUser.get_updated_version_of_mapping_dict(
            mapping_dict=self.mapping_dict,
            deleted_from_session_subjects=self.deleted_from_session_subjects,
        )

        print("##########################")
        print(updated_mapping_dict)
        print(self.deleted_from_session_subjects)
        print(self.mapping_dict)
        updated_mapping_dict_str: str = InterfaceUser.get_updated_mapping_dict_str(
            updated_mapping_dict
        )


        while input_user not in updated_mapping_dict:
            input_user = input(
                f"Wrong input ; choose from this list :\n {updated_mapping_dict_str}"
            )

        mapped_key:str = updated_mapping_dict[input_user] # From number to actual subject name
        self.propose_a_page(subject=mapped_key)

    def main(self):

        menu = InterfaceUser.create_menu(
            updated_data_structure=self.updated_data_structure,
            count_dict=self.count_dict,
        )

        self.mapping_dict = InterfaceUser.create_mapping_user_choices(menu=menu)

        menu += "\n:"

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
                    self.case_all_subjects_from_current_scope(user_input)


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
            [f"{key_} : {value}" 
             for key_, value 
             in updated_mapping_dict.items() ]
        )
