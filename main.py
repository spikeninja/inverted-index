import re
import pickle

from typing import List, Tuple
from bisect import insort

class Preprocessor:
    def __init__(self):
        pass

    def clear_test(self, text: str) -> str:
        """
        Delete unneeded letters and symbols from text
        using re module.
        """
        # every char except alphabet excluded
        cleaned_str = re.sub('[^a-z\s]+', '',str_arg,flags=re.IGNORECASE)
        # multiple spaces replaced by single
        cleaned_str = re.sub('(\s+)', ' ',cleaned_str)
        # lowercasing string
        cleaned_str = cleaned_str.lower()

        return cleaned_str

    def tokenize_text(self, text: str) -> List[str]:
        """
        Takes string and returns its splitted version.
        """
        return text.split()


class Serializer:
    def __init__(self):
        pass

    def serialize(obj: object, path: str):
        pass

    def deserialize(path: str) -> object:
        pass


class DocDict:
    def __init__(self):
        self.dictionary = defaultdict(lambda x: [])

    def add(self, key, value):
        insort(self.dictionary.setdefault(key, []), value)

    def sort(self, key):
        self.dictionary[key].sort()



class InvertedIndex:
    def __init__(self):
        pass

    def create_index(text: str):
        pass

    def __construct_index(self):
        pass

    @classmethod
    def merge(d1, d2):
        pass

def main():
    pass


if __name__ == '__main__':
    main()
