import random
from typing import Optional
from collections import defaultdict, deque


class DictQueueStructure:
    """
    Will contains the main data structure ;
    a dictionnary with n keys (n being the number of main subject pages), and as values queues (following the FIFO principle, first in, first out)
    will contains a deque of dictionnaries, with the page name as key and the page url as value
    """

    def __init__(self, data_structure=defaultdict(deque)):
        self.data_structure = data_structure

    def random_shuffle(self, key_: Optional[str] = None):
        if key_ is not None:
            random.shuffle(self.data_structure.get(key_))

        else:  # Full shuffle
            key_: str
            for key_ in self.data_structure:
                random.shuffle(self.data_structure.get(key_))

    def shift_last_to_first(self, key_: str):
        dequeue_: deque = self.data_structure.get(key_)
        dequeue_.appendleft(dequeue_.pop())

    def randomly_resinsert_last_element(self, key_: str):
        dequeue_: deque = self.data_structure.get(key_)
        element_to_reinsert: dict = dequeue_.pop()
        new_index = random.randint(0, len(dequeue_))
        dequeue_.insert(new_index, element_to_reinsert)

    def insert_new_page(self, key_: str, new_page: dict):
        dequeue_: deque = self.data_structure.get(key_)
        dequeue_.appendleft(new_page)
