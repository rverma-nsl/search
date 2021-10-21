import os
import time
import sys
import numpy as np
from bert_serving.client import BertClient
from functools import reduce


sys.path.append("..")
from config import TOP_K
from logs import LOGGER



bc = BertClient()

def normaliz_vec(vec_list):
    for i in range(len(vec_list)):
        vec = vec_list[i]
        square_sum = reduce(lambda x,y:x+y, map(lambda x:x*x ,vec))
        sqrt_square_sum = np.sqrt(square_sum)
        coef = 1/sqrt_square_sum
        vec = list(map(lambda x:x*coef, vec))
        vec_list[i] = vec
    return vec_list

def search_in_milvus(bet_type, query_sentence,milvus_cli, mysql_cli):
    try:
        query_data = [query_sentence]
        vectors = bc.encode(query_data) 
        query_list = normaliz_vec(vectors.tolist())
        LOGGER.info("Successfully insert query list")
        results = milvus_cli.search_vectors(bet_type,query_list,TOP_K)
        vids = [str(x.id) for x in results[0]]
        print("-----------------", vids)
        ids,title,text= mysql_cli.search_by_milvus_ids(vids, bet_type)
        distances = [x.distance for x in results[0]]
        return ids,title, distances
    except Exception as e:
        LOGGER.error(" Error with search : {}".format(e))
        sys.exit(1)