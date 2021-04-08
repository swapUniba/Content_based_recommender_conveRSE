import pandas as pd
import numpy as np
from gensim.similarities import MatrixSimilarity
from gensim.models import TfidfModel
from gensim.corpora import Dictionary

def create_model_tfidf_model(documents, model_name, matrix_name, dic_name):
    dictionary = Dictionary(documents)
    corpus = [dictionary.doc2bow(doc) for doc in documents]
    tfidfmodel = TfidfModel(corpus)
    index = MatrixSimilarity(tfidfmodel[corpus], num_features=len(dictionary))
    index.save(matrix_name)
    tfidfmodel.save(model_name)
    dictionary.save(dic_name)
    return tfidfmodel, index, dictionary


def load_tfidf_model(documents, model_name, matrix_name, dic_name):
    try:
        tfidfmodel = TfidfModel.load(model_name)
        index = MatrixSimilarity.load(matrix_name)
        dictionary = Dictionary.load(dic_name)
    except Exception:
        tfidfmodel, index, dictionary = create_model_tfidf_model(documents=documents, model_name= model_name, matrix_name= matrix_name, dic_name= dic_name)
    return tfidfmodel, index, dictionary


def print_res_tfidf(token_strings, documents, titles, IDs, dictionary, tfidfmodel, index, prefIDs):
    if dictionary is None or tfidfmodel is None or index is None:
        tfidfmodel, index, dictionary = load_tfidf_model(documents,"TFIDF/tfidf_model", "TFIDF/matrix_tfidf", "TFIDF/dictionary_tfidf")
    sims = []
    try:
        for string in token_strings:
            query = dictionary.doc2bow(string)
            vec_bow_tfidf = tfidfmodel[query]
            sim = index.get_similarities(vec_bow_tfidf)
            sims.append(sim)
    except Exception:
        query = dictionary.doc2bow(token_strings)
        vec_bow_tfidf = tfidfmodel[query]
        sim = index.get_similarities(vec_bow_tfidf)
        sims.append(sim)
    sim = np.asarray(sims).mean(axis=0)
    cos_sim_s, titles, IDs = zip(*sorted(zip(sim, titles, IDs), reverse=True))
    outputW2V = []
    rank = 1
    for i in range(5 + len(token_strings)):
        if len(outputW2V) == 5:
            break
        if prefIDs is not None:
            if IDs[i] in prefIDs:
                continue
        outputW2V.append([rank, titles[i], cos_sim_s[i]])
        rank += 1
    print("--------------TF-IDF--------------")
    df = pd.DataFrame(outputW2V, columns=["rank", "title", "cosine_similarity"])
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    print(df)