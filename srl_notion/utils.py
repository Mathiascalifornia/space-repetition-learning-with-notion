import pickle
import pathlib
from typing import Any


def load_pickle(path_object: pathlib.Path) -> Any:
    with open(path_object, "rb") as f:  # rb -> Read Binary
        return pickle.load(f)


def save_pickle(object_: Any, path_to_save: pathlib.Path) -> None:
    with open(path_to_save, "wb") as f:
        pickle.dump(object_, f)
