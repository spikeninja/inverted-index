import re
import pickle
import os

from multiprocessing import Process

from typing import List, Tuple
from bisect import insort
from collections import defaultdict
from time import time

def _default():
        return defaultdict(0)

class Preprocessor:
    def __init__(self):
        pass

    def clear(self, text: str) -> str:
        """
        Delete unneeded letters and symbols from text
        using re module.
        """
        # every char except alphabet excluded
        cleaned_str = re.sub('[^a-z\s]+', '', text, flags=re.IGNORECASE)
        # multiple spaces replaced by single
        cleaned_str = re.sub('(\s+)', ' ',cleaned_str)
        # lowercasing string
        cleaned_str = cleaned_str.lower()

        return cleaned_str

    def tokenize(self, text: str) -> List[str]:
        """
        Takes string and returns its splitted version.
        """
        return text.split()


class Serializer:
    def __init__(self):
        pass

    def serialize(self, obj: object, filename: str):
        with open(filename, 'wb') as f:
            pickle.dump(obj, f)

    def deserialize(self, filename: str) -> object:
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        return data


class DocDict:
    def __init__(self):
        self.dictionary = defaultdict(_default)


    def add(self, key, value):
        insort(self.dictionary.setdefault(key, []), value)

    def add_unexist(self, key, value):
        if self.dictionary.get(key):
            if not value in self.dictionary.get(key):
                insort(self.dictionary.setdefault(key, []), value)
        else:
            insort(self.dictionary.setdefault(key, []), value)

    def sort(self, key):
        self.dictionary[key].sort()

    def __add__(self, other):
        k1 = set(self.dictionary.keys())
        k2 = set(other.dictionary.keys())
        inter = k1 & k2
        for key in inter:
            for el in other.dictionary[key]:
                self.add_unexist(key, el)
        k2_m = k2 - inter
        for key in k2_m:
            self.dictionary[key] = other.dictionary[key]

        return self

    def __reduce__(self):
        return (DocDict, (self.dictionary, ))



class InvertedIndex:
    def __init__(self, preprocessor: Preprocessor, serializer: Serializer):
        self.index = dict()
        self.preprocessor = preprocessor
        self.serializer = serializer
        self.buffer = ''

    def create_index(self, path: str):
        for file in os.listdir(path):
            with open(os.path.join(path, file), 'r') as f:
                self.buffer += ' ' + f.read()

            #print(os.path.join(self.dir_path, file))

            self.buffer = self.preprocessor.clear(self.buffer)
            tokens = self.preprocessor.tokenize(self.buffer)

            for token in tokens:
                if token not in self.index:
                    dd = DocDict()
                    for idx in self.get_word_indexes(tokens, token):
                        dd.add_unexist(file, idx)
                    self.index.setdefault(token, dd)
                else:
                    for idx in self.get_word_indexes(tokens, token):
                        self.index[token].add_unexist(file, idx)
            self.buffer = ''

    def search(self, word: str):
        return self.index[word].dictionary


    def get_word_indexes(self, tokens: List[int], word: str) -> List[int]:
        result = [i for i in range(len(tokens)) if tokens[i] == word]
        return result

    def serialize(self, path: str):
        self.serializer.serialize(self.index, path)

    def deserialize(self, path: str):
        self.index = self.serializer.deserialize(path)

    @classmethod
    def merge(d1, d2):
        keys_d1 = set(d1.keys())
        keys_d2 = set(d2.keys())
        inter = keys_d1 & keys_d2
        for key in inter:
            d1[key] += d2[key]
        d2_m = keys_d2 - inter
        for key in d2_m:
            d1[key] = d2[key]

def execution(ii: InvertedIndex, paths: List[str], lower_bound: int, upper_bound: int):
    for i in range(lower_bound, upper_bound):
        ii.create_index(paths[i])

def parallel_creation(ii: InvertedIndex, paths: List[str], thread_amount: int):
    N = len(paths)
    processes = []
    for i in range(thread_amount):
        p = Process(target=execution, args=(ii, paths, i*(N//thread_amount), (i+1)*(N//thread_amount)))
        p.start()
        processes.append(p)
        #execution(ii, paths, i*(N/thread_amount), (i+1)*(N/thread_amount))
    return processes


def main():
    preprocessor = Preprocessor()
    serializer = Serializer()
    ii = InvertedIndex(preprocessor, serializer)

    paths = [
    'data/my_variant/train/pos',
    'data/my_variant/train/neg',
    'data/my_variant/train/unsup',
    'data/my_variant/test/pos',
    'data/my_variant/test/neg',
    ]

    start = time()
    execution(ii, paths, 0, len(paths))
    duration = time() - start

    print("Duration (consistent): ", duration)

    start = time()
    processes = parallel_creation(ii, paths, 5)
    for p in processes:
        p.join()
    duration = time() - start

    print("Duration (parallel): ", duration)
    #print(ii.search('so'))


if __name__ == '__main__':
    main()
