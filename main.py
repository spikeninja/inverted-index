import re
import pickle
import os
import argparse

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

    def clear(self, text: str):
        """
        Delete unneeded letters and symbols from text
        using re module.
        """

        cleaned_str = re.sub('[^a-z\s]+', '', text, flags=re.IGNORECASE)
        cleaned_str = re.sub('(\s+)', ' ',cleaned_str)
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
        """
        Serializes object to the particular file.
        """

        with open(filename, 'wb') as f:
            pickle.dump(obj, f)

    def deserialize(self, filename: str) -> object:
        """
        Deserializing object/data from particular file.
        """

        with open(filename, 'rb') as f:
            data = pickle.load(f)
        return data


class DocDict:
    def __init__(self):
        self.dictionary = defaultdict(_default)


    def add(self, key: str, value: int):
        """
        Adding key-value pair to the dictionary.
        """

        insort(self.dictionary.setdefault(key, []), value)

    def add_unexist(self, key: str, value: int):
        """
        Adding key-value pair to the dictionary only if 
        dictionary does not have it.
        """

        if self.dictionary.get(key):
            if not value in self.dictionary.get(key):
                insort(self.dictionary.setdefault(key, []), value)
        else:
            insort(self.dictionary.setdefault(key, []), value)

    def __add__(self, other):
        """
        Overloading '+' operator as an union operation
        between two dictionaries.
        """

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
        """
        Creates inverted index by iterating over folder
        files, preprocessing text in the files and save it.
        """

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
        """
        Returns file_name:[list of indexes] pair of particular word.
        """
        return self.index[word].dictionary


    def get_word_indexes(self, tokens: List[int], word: str) -> List[int]:
        """
        Returns all indexes of word which encounters in the tokenized text.
        """

        result = [i for i in range(len(tokens)) if tokens[i] == word]
        return result

    def serialize(self, path: str):
        """
        Serializes index to the particular file.
        """
        self.serializer.serialize(self.index, path)

    def deserialize(self, path: str):
        """
        Deserializing index from the file.
        """
        self.index = self.serializer.deserialize(path)

    @staticmethod
    def merge(d1: dict, d2: dict):
        """
        Mergest two dictionaries.

        In result it returns union of dictionaries.
        """

        keys_d1 = set(d1.keys())
        keys_d2 = set(d2.keys())
        inter = keys_d1 & keys_d2
        for key in inter:
            d1[key] += d2[key]
        d2_m = keys_d2 - inter
        for key in d2_m:
            d1[key] = d2[key]

def execution(ii: InvertedIndex, paths: List[str], lower_bound: int, upper_bound: int):
    """
    Executes creating index operation on particular paths constrained by
    lower_bound and upper_bound.
    """

    for i in range(lower_bound, upper_bound):
        ii.create_index(paths[i])

def parallel_creation(ii: InvertedIndex, paths: List[str], process_amount: int):
    """
    Parallel creation of InvertedIndex object.
    """

    N = len(paths)
    processes = []
    for i in range(process_amount):
        p = Process(target=execution, args=(ii, paths, i*(N//process_amount), (i+1)*(N//process_amount)))
        p.start()
        processes.append(p)
    return processes


def main():
    preprocessor = Preprocessor()
    serializer = Serializer()
    ii = InvertedIndex(preprocessor, serializer)

    parser = argparse.ArgumentParser()
    parser.add_argument("proc", help="max amount of processes to use",
                        type=int, default=5)
    args = parser.parse_args()
    AMOUNT_OF_PROCESSES = args.proc

    paths = [
    #'data/my_variant/train/pos',
    #'data/my_variant/train/neg',
    #'data/my_variant/train/unsup',
    #'data/my_variant/test/pos',
    #'data/my_variant/test/neg',
    'data/my_variant/all/1',
    'data/my_variant/all/2',
    'data/my_variant/all/3',
    'data/my_variant/all/4',
    'data/my_variant/all/5',
    'data/my_variant/all/6',
    'data/my_variant/all/7'
    ]

    start = time()
    execution(ii, paths, 0, len(paths))
    duration = time() - start

    print("Duration (consistent): ", duration)

    ii2 = InvertedIndex(preprocessor, serializer)

    for i in range(2, AMOUNT_OF_PROCESSES + 1):
        ii = InvertedIndex(preprocessor, serializer)
        start = time()
        processes = parallel_creation(ii, paths, i)
        for p in processes:
            p.join()
        #InvertedIndex.merge(ii2.index, ii.index)
        duration = time() - start

        print(f"Duration ({i} processes): ", duration)

    #print(ii.search('so'))


if __name__ == '__main__':
    main()
