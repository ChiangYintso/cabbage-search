import sys
from typing import IO, DefaultDict, List, KeysView
from collections import defaultdict
from math import log10
import os
import numpy as np


def get_term_frequencies_n(file: IO) -> DefaultDict[str, int]:
    result: DefaultDict[str, int] = defaultdict(int)
    lines = file.readlines()
    for line in lines:
        terms = line.split('/')
        for term in terms:
            result[term] += 1
    return result


def get_tf_l(tf_n: int) -> float:
    return 1 + log10(tf_n)


def get_idf_t(N: int, df: np.array) -> np.array:
    return np.log10(N / df)


def get_tf_vec(term_doc: DefaultDict[str, int], terms: KeysView[str]) -> np.array:
    arr = np.zeros(len(terms), dtype=np.float)
    for i, k in enumerate(terms):
        arr[i] = term_doc[k]
    return arr


def get_df_n(prefix: str, docs: List[str], term: str) -> int:
    count = 0
    for docpath in docs:
        with open(f'{prefix}{docpath}', encoding='utf-8') as f:
            text = ''.join(f.readlines())
            if term in text:
                count += 1
    return count


def get_df_list_n(prefix: str, docs, terms):
    arr = np.zeros(len(terms), dtype=np.float)
    for i, term in enumerate(terms):
        arr[i] = get_df_n(prefix, docs, term)
    return arr


def normalise(idf_vec: np.array) -> np.array:
    return idf_vec / np.sqrt(sum(idf_vec * idf_vec))


def cos_dis(v1: np.array, v2: np.array) -> float:
    return np.sum(v1 * v2) / (
            np.sum(v1 * v1) ** 0.5 * np.sum(v2 * v2) ** 0.5)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('usage: python cos_distance.py <prefix> <doc_id1> <doc_id2>')
        exit(-1)
    docs = os.listdir(f'build/{sys.argv[1]}_terms')
    N = len(docs)

    term_path1 = f'build/{sys.argv[1]}_terms/{sys.argv[1]}_{"%05d" % int(sys.argv[2])}.txt'
    term_path2 = f'build/{sys.argv[1]}_terms/{sys.argv[1]}_{"%05d" % int(sys.argv[3])}.txt'
    tf1_n: DefaultDict[str, int]
    tf2_n: DefaultDict[str, int]
    terms: KeysView[str]
    with open(term_path1, encoding='utf-8') as f1, open(term_path2, encoding='utf-8') as f2:
        tf1_n = get_term_frequencies_n(f1)
        tf2_n = get_term_frequencies_n(f2)
        terms = tf1_n.keys() or tf2_n.keys()

    tf_vec_1 = get_tf_vec(tf1_n, terms)
    tf_vec_2 = get_tf_vec(tf2_n, terms)

    df_vec: np.array = get_df_list_n(f'build/{sys.argv[1]}_terms/', docs, terms)
    idf_vec: np.array = get_idf_t(N, df_vec)
    idf_vec = normalise(idf_vec)

    tfxidf_vec1 = tf_vec_1 * idf_vec
    tfxidf_vec2 = tf_vec_2 * idf_vec
    cos_similarity = cos_dis(tfxidf_vec1, tfxidf_vec2)
    print('similarity: ', cos_similarity)

    for i in range(1, 3):
        print(f'doc{i}: ')
        with open(f'build/{sys.argv[1]}_article/{sys.argv[1]}_{"%05d" % int(sys.argv[i + 1])}.txt',
                  encoding='utf-8') as f:
            for line in f.readlines():
                print(line)
        print()
