"""
Defines the Doc class to be used by getRelationalVerbAnnotations.py.

Author: Serena G. Lotreck
"""
class Doc:

    def __init__(self, doc_dict):
        """
        doc_dict: dygiepp-formatted dict of predictions
        """
        # Get sentences as one list of tokens 
        self.unraveled_sentences = []
        for sentence in doc_dict['sentences']:
            for word in sentence: 
                self.unraveled_sentences.append(word)

        self.sentences = doc_dict['sentences']
        self.relations = doc_dict['predicted_relations']
        self.doc_key = doc_dict['doc_key']
        self.anns = []

    @staticmethod
    def get_verb(sentence, ent1, ent2):
        """
        Get the verb between two entities. 

        parameters:
            sentence, list of str: tokenized sentence 
            ent1, list: [start_tok, end_tok] where numbers are in terms of 
        """


    def get_anns(self):
        """
        Get annotations for this doc as a list of list, where each annotation
        takes the form:

        ["sentence...doc_key", "T<number>", "TYPE", "start", "end", "TEXT"]

        where the start and end are in reference to the CHARACTER INDICES of 
        this particular document.

        There will be multiple annotations with the same "sentence...doc_key"
        first element, because there are three annotations for each relation, 
        that each need to end up on a separate line of the final .ann file: 
        one for each entity, and one for the relational verb.
        """
        num_entries = 0
        for relation_list, sentence in zip(self.relations, self.sentences):
            
            # Get a string with the sentence and doc key
            sentence_str = " ".join(sentence) + self.doc_key

            # Go through relations in the sentence 
            for relation in relation_list:

                # Get the entities 

                # Get verb 

