import re
import pickle
import os

from typing import List, Tuple
from bisect import insort
from collections import defaultdict

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

    def deserialize(self, path: str) -> object:
        with open(filename, 'rb') as f:
            data = pickle.load(filename)
        return data


class DocDict:
    def __init__(self):
        self.dictionary = defaultdict(lambda x: [])

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
        pass

def main():
    preprocessor = Preprocessor()
    serializer = Serializer()
    ii = InvertedIndex(preprocessor, serializer)
    ii.create_index('data/test')
    #print(ii.index)
    print(ii.search('so'))
    #print(ii.index['main'].dictionary)
    ii.serialize('this.ii')


if __name__ == '__main__':
    main()
