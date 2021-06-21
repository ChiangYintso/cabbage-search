# -*- coding: utf-8 -*-
import os
import random
import sys
from typing import KeysView, List
import numpy as np

from cos_distance import get_term_frequencies_n, get_df_list_n, get_idf_t, normalise, get_tf_vec, cos_dis


def kmeans(vectors: List[np.array], k=20):
    centroids = [np.array(vectors[random.randint(0, len(vectors) - 1)]) for _ in range(k)]
    classes = [[] for _ in range(k)]
    for _ in range(10):
        classes = [[] for _ in range(k)]
        for v_idx, v in enumerate(vectors):
            min_dis = 9999999999999999
            idx = -1
            for j, centroid in enumerate(centroids):
                dis = cos_dis(v, centroid)
                if idx == -1 or min_dis > dis:
                    idx = j
                    min_dis = dis
            classes[idx].append(v_idx)
        for j in range(k):
            if len(classes[j]) == 0:
                centroids[j] = np.array(vectors[random.randint(1, len(vectors))])
            else:
                centroids[j] = np.zeros(len(vectors[0]), dtype=float)
                for v_idx in classes[j]:
                    centroids[j] += vectors[v_idx]
                centroids[j] /= len(classes[j])

    assert len(classes) == len(centroids)
    arr = list(zip(classes, centroids))
    arr.sort(key=lambda x: -len(x[0]))
    print(arr[:3])

    for i, (cls, centroid) in enumerate(arr[:3]):
        li = []
        for v_idx in cls:
            dis = cos_dis(vectors[v_idx], centroid)
            li.append((v_idx, dis))
        li.sort(key=lambda x: x[1])
        print(f'class {i}:')
        print(li[:5])


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: python kmeans_cluster.py <prefix>')
        exit(-1)
    docs = os.listdir(f'build/{sys.argv[1]}_terms')
    N = len(docs)

    terms: KeysView[str] = None
    tfs = []
    for i in range(N):
        term_path = f'build/{sys.argv[1]}_terms/{sys.argv[1]}_{"%05d" % i}.txt'
        with open(term_path, encoding='utf-8') as f:
            tf_n = get_term_frequencies_n(f)
            if terms is None:
                terms = tf_n.keys()
            else:
                term = terms or tf_n.keys()
            tfs.append(tf_n)

    df_vec: np.array = get_df_list_n(f'build/{sys.argv[1]}_terms/', docs, terms)
    idf_vec: np.array = get_idf_t(N, df_vec)
    idf_vec = normalise(idf_vec)

    tfxidfs = [get_tf_vec(tf, terms) * idf_vec for tf in tfs]
    kmeans(tfxidfs)
