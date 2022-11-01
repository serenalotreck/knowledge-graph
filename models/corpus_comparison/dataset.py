"""
Classes to store and manipulate annotated NLP datasets.

Author: Serena G. Lotreck
"""
from nltk.util import ngrams


class Document():
    """
    Stores the vocabulary, annotations, and full text for a single document.
    """
    def __init__(self, doc_dict ):
        """
        Initialize a Document instance from a dygiepp-formatted dict
        """
        self.doc_key = doc_dict["doc_key"]
        self.full_text = " ".join([" ".join(i) for i in doc_dict["sentences"]])
        self.sentences = doc_dict["sentences"]
        self.tokens = [word for sent in doc_dict["sentences"] for word in sent]
        self.uni_vocab = set(self.tokens)
        self.ent_anns = doc_dict["ner"]
        self.rel_anns = doc_dict["relations"]


    def get_doc_vocab(self):
        """
        Returns a dictionary with unigram, bigram, and trigram vocab for the
        document
        """
        unigrams = list(self.uni_vocab)
        bigrams = ['_'.join(ngr) for ngr in ngrams(unigrams, 2)]
        trigrams = ['_'.join(ngr) for ngr in ngrams(unigrams, 3)]

        vocab = {'unigrams': unigrams, 'bigrams': bigrams, 'trigrams':
                trigrams}

        return vocab


class Dataset():
    """
    A class to store instances of Documents that occur together in a dataset.
    """
    def __init__(self, dataset_name='', processed_dataset=[]):
        """
        Takes a list of dictionaries from the same dataset and constructs
        Document objects for them.
        """
        self.dataset_name = dataset_name
        self.docs = []
        for doc in processed_dataset:
            self.docs.append(Document(doc))

    def get_dataset_name(self):
        return self.dataset_name

    def get_dataset_sents(self):
        """
        Returns a list of sentences in the dataset, where each sentence is a
        list of strings.
        """
        sents = []
        for doc in self.docs:
            sents.extend(doc.sentences)
        return sents

    def get_dataset_vocab(self):
        """
        Gets a dictionary where keys are unigrams, bigrams, and trigrams, and
        the values are sets of the volcabulary for each type of ngram. Also
        sets the attribute vocab for this dataset.
        """
        vocab = {'unigrams':[], 'bigrams':[], 'trigrams':[]}
        for doc in self.docs:
            doc_vocab = doc.get_doc_vocab()
            for key in vocab.keys():
                vocab[key].extend(doc_vocab[key])
        vocab = {k: set(v) for k, v in vocab.items()}
        self.vocab = vocab
        return self.vocab
