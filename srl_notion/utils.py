import pickle 
import pathlib
from typing import Any


def load_pickle(path_object:pathlib.Path) -> Any:
    with open(path_object, "rb", # rb -> Read Binary 
              encoding="utf-8") as f:
        return pickle.load(f)
    
def save_pickle(object_:Any, path_to_save:pathlib.Path) -> None:
    with open(path_to_save, "wb", encoding="utf-8") as f:
        pickle.dump(object_, f)
