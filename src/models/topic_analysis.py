import statistics
import pandas as pd
import numpy as np

from gensim.corpora import Dictionary
from gensim.models import LsiModel
from gensim.models.ldamulticore import LdaModel
from gensim.models.wrappers import LdaMallet

params = {"num_topics": 10, "chunksize": 500}


def _load_model(type, fname='../../model/'):
    try:
        if type == 'lsi':
            return LsiModel.load(fname)
        elif type == 'lda':
            return LdaModel.load(fname)
        elif type == 'mallet':
            return LdaMallet.load(fname)
    except:
        return None


def _save_model(model, fname):
    model.save(fname)


def create_doc_term_matrix(docs):
    id2word = Dictionary(documents=docs)
    doc_term_matrix = [id2word.doc2bow(doc) for doc in docs]

    return doc_term_matrix, id2word


def get_lsi_model(doc_term_matrix, id2word, fname):
    if fname is not None:
        try:
            return LsiModel.load(fname)
        except:
            pass

    lsi_model = LsiModel(
        corpus=doc_term_matrix,
        id2word=id2word,
        num_topics=params['num_topics'],
        chunksize=params['chunksize']
    )

    _save_model(lsi_model, fname)

    return lsi_model


def get_lda_model(doc_term_matrix, id2word, fname):
    try:
        lda_model = LdaModel.load(fname)
    except:
        lda_model = LdaModel(
            corpus=doc_term_matrix,
            id2word=id2word,
            num_topics=params['num_topics'],
            chunksize=params['chunksize'],
            random_state=100,
            update_every=1,  # online iterative learning
            passes=2,
            distributed=False,
            # alpha='auto',
            per_word_topics=True
        )

    _save_model(lda_model, fname=fname)

    return lda_model


def get_lda_mallet_model(doc_term_matrix, id2word, fname):
    mallet_path = '../../model/mallet-2.0.8/bin/mallet'

    if fname is not None:
        try:
            LdaMallet(fname)
        except:
            pass

    lda_mallet = LdaMallet(
        mallet_path=mallet_path,
        corpus=doc_term_matrix,
        id2word=id2word,
        num_topics=10
    )

    _save_model(lda_mallet, fname=fname)

    return lda_mallet


def get_document_topics(model, doc_term_matrix, docs):
    """ scores topics to sentences first, then picks the mode for the doc and creates mode, sentence topics, and sentence topics with probabilities. """
    results = []

    i, j = 0, 0
    for doc in docs:
        j = j + len(doc)
        doc_topic_list = model[doc_term_matrix][i:j+1]
        i = j
        in_doc_topic_prob_list = [
            max(sent_topic_list, key=lambda x: x[1]) for sent_topic_list in doc_topic_list]
        doc_topics = ",".join(
            [topic for topic, prob in in_doc_topic_prob_list])
        doc_topic_mode = statistics.mode(
            [topic for topic, prob in in_doc_topic_prob_list])

        results.append(doc_topic_mode, doc_topics, in_doc_topic_prob_list)

    return results
