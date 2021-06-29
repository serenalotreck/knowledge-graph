"""
Defines the Doc class to be used by getRelationalVerbAnnotations.py.

scispaCy medium model should be installed in order to use this class.

Author: Serena G. Lotreck
"""
import spacy

class Doc:

    def __init__(self, doc_dict, out_loc):
        """
        doc_dict: dygiepp-formatted dict of predictions
        out_loc, str: place to save files, absolute path
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
        self.out_loc = out_loc


    @staticmethod
    def get_verbs(sentence):
        """
        Get the verbs in a sentence. 

        parameters:
            sentence, str: sentence in which to find verbs
            nlp, spaCy nlp object: spaCy instance to use for tokenization
        
        returns: 
            verbs, list of tuple: contains (verb_text, token_index) for each verb
        """
        # Do POS tagging
        sent = nlp(sentence)

        # Get verbs 
        verbs = []
        token_idx = 0 # spaCy gives a POS to every token
        for token in sent:
            if token.pos_ == 'VERB':
                verbs.append((token.text, token_idx)) # Trusting that spaCy tokenization is consistent
        
        return verbs


    @staticmethod
    def get_between_verbs(relation, verbs):
        """
        Get the verbs that come between two entities in a relation.

        parameters:
            relation, list: [start_tok1, end_tok1, start_tok2, end_tok2, "TYPE", logit, softmax]
            verbs, list of tuple: [(verb, token_idx), ...]

        returns:
            relation, list: 
                [start_tok1, end_tok1, start_tok2, end_tok2, "TYPE", logit, softmax, verb1_tok_idx, verb2_tok_idx...]
        """
        between_verbs = []
        if relation[1] < relation[3]:
            for verb in verbs:
                if relation [1] < verb[1] < relation[3]:
                    between_verbs.append(verb)

        elif relation[1] > relation[3]:
            for verb in verbs: 
                if relation [3] < verb[1] < relation[1]:
                    between_verbs.append(verb)

        for verb in between_verbs:
            relation.append(verb[1])

        return relation


    def get_anns(self):
        """
        Get annotations for this doc as a list of list, where each annotation
        takes the form:

        ["sentence", "T<number>", "TYPE", "start", "end", "TEXT"]

        or

        ["sentence", R<number>, "TYPE", "Arg1:T<number>", "Arg2:T<number>"]

        where the start and end for entities are in reference to the CHARACTER 
        INDICES of this particular document.

        There will be multiple annotations with the same "sentence"
        first element, because there are four annotations for each relation, 
        that each need to end up on a separate line of the final .ann file: 
        one for each entity, and one for the relational verb. There can 
        additionally be multiple relations in a sentence.
        
        returns: list of annotations
        """
        # Initialize spaCy object that will be used to tokenize
        nlp = spacy.load("en_core_sci_sm")

        # Get annotations
        num_T = 0
        num_R = 0
        num_chars = 0 # Keeps track of how many total characters were in previous sentences 
        anns = []
        for relation_list, sentence in zip(self.relations, self.sentences):
            
            # Get a string with the sentence
            sentence_str = " ".join(sentence)

            # Get all verbs in a sentence
            verbs = get_verbs(sentence, nlp)

            # Go through relations in the sentence 
            for relation in relation_list:

                # Check if verbs come between entities
                between_verbs = get_between_verbs(relation, verbs)

                # Get the annotations 
                ## Entities 
                ### Entity indices are in terms of tokens in the whole document
                ent_IDs = []
                for ent_num in (1, 3):
                    num_T += 1
                    ent_start = sum(len(i) for i in self.unraveled_sentences[:relation[ent_num]])
                    ent_text = " ".join(self.unraveled_sentences[relation[ent_num-1]:relation[ent_num]+1])
                    ent_len = len(ent_text)
                    ent_end = ent_start + ent_len
                    annotation = [sentence_str, f'T{num_T}', "ENTITY", ent_start, end_end, ent_text]  
                    anns.append(annotation)
                    ent_IDs.append(f'T{num_T}')

                ## Text-bound relational verbs
                ### Verb indices are in terms of this single sentence
                num_T += 1
                rel_start = num_chars + sum(len(i) for i in sentence[:relation[7]])
                rel_text = " ".join(sentence[relation[7]:relation[-1]+1])
                rel_len = len(rel_text)
                rel_end = rel_start + rel_len
                annotation = [sentence_str, f'T{num_T}', relation[4], rel_start, rel_end, rel_text]
                anns.append(annotation)

                ## Non-text-bound relations
                num_R += 1
                annotation = [sentence_str, f'R{num_R}', relation[4], f'Arg1:{entIDs[0]}', f'Arg2:{entIDs[1]}']
                anns.append(annotation)

            num_chars += len(sentence_str) + 1 # To account for newline between each sentence

        self.anns += anns

        return self.anns


    def write_ann(self):
        """
        Write out .ann file for this document.
        """
        ann_string = ''

        for ann in self.anns:
            if ann[1][0] == 'T':
                ann_string += f'{ann[1]}\t{ann[2]} {ann[3]} {ann[4]}\t{ann[5]}\n'
            elif ann[1][0] == 'R':
                ann_string += f'{ann[1]}\t{ann[2]} {ann[3]} {ann[4]}\n'

        with open(f'{self.out_loc}/{self.doc_key}_rel_sentences.ann', 'w') as myfile:
            myfile.write(ann_string)


    def write_txt(self):
        """
        Write out corresponding .txt file for this document. 
        Only contains sentences that have relations in them.
        """
        sentences = set([ann[0] for ann in self.anns])
        sentences_str = '\n'.join(sentences)

        with open(f'{self.out_loc}/{self.doc_key}_rel_sentences.txt', 'w') as myfile:
            myfile.write(sentences_str)

