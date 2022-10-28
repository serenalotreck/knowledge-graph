"""
Classes to store and manipulate annotated NLP datasets.

Author: Serena G. Lotreck
"""
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
        self.vocab = set(self.tokens)
        self.ent_anns = doc_dict["ner"]
        self.rel_anns = doc_dict["relations"]


    def get_doc_vocab(self):
        return self.vocab


class Dataset():
    """
    A class to store instances of Documents that occur together in a dataset.
    """
    def __init__(self, dataset_name, processed_dataset):
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

    def get_dataset_vocab(self):
        vocab = []
        for doc in self.docs:
            vocab += doc.get_doc_vocab()

        return set(vocab)
