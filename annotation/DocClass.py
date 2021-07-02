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
        self.annotated_sentences = ''
        self.relation_verbs = []
        self.out_loc = out_loc


    @staticmethod
    def get_verbs(sentence, nlp):
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
            token_idx += 1 
        return verbs


    def get_rel_verb_anns(self, relation, num_T, anns, sentence, sentence_str):
        """
        Get relational verb annotation for a relation.
        This function is badly compartmentalized and I know it, 
        just wanted to clean up the parent function a bit.

        returns:
            (num_T, anns): (int, list)
        """
        if len(relation) >= 8:
            num_T += 1
            # Get relation start within the annotated sentences using the per-sentence index 
            rel_start = len(self.annotated_sentences) + \
                        len(" ".join(sentence[:relation[7]]))
            if rel_start != 0:
                rel_start += 1 # Account for the trailing spaces not added by " ".join()
            rel_text = " ".join(sentence[relation[7]:relation[-1]+1])
            rel_len = len(rel_text)
            rel_end = rel_start + rel_len
            annotation = [sentence_str, f'T{num_T}', relation[4], rel_start, rel_end, rel_text]
            anns.append(annotation)
    
        return (num_T, anns)

    
    def get_entity_anns(self, relation, num_T, anns, sentence, sentence_str):
        """
        Get entity annotations for a relation.
        This function is badly compartmentalized and I know it, 
        just wanted to clean up the parent function a bit.
        
        returns:
            (ent_IDs, num_T, anns): (list, int, list)
        """
        ent_IDs = []
        for ent_num in (0, 2):
            num_T += 1
            # Convert entity index to a per-sentence index
            current_sent_idx = self.sentences.index(sentence) # Assumes all sentences are unique
            previous_sent_token_num = sum(len(i) for i in self.sentences[:current_sent_idx])
            per_sent_token_start_idx = relation[ent_num] - previous_sent_token_num
            # Get entity start within the annotated sentences using the per-sentence index 
            ent_start = len(self.annotated_sentences) + \
                        len(" ".join(sentence[:per_sent_token_start_idx]))
            if ent_start != 0 and ent_start != len(self.annotated_sentences):
                ent_start += 1 # Account for the trailing spaces not added by " ".join()
            # Get entity text
            ent_text = " ".join(self.unraveled_sentences[relation[ent_num]:relation[ent_num+1]+1])
            # Get entity end 
            ent_len = len(ent_text)
            ent_end = ent_start + ent_len
            # Generate annotation 
            annotation = [sentence_str, f'T{num_T}', "ENTITY", ent_start, ent_end, ent_text]  
            # Update ID list and text-bound annotation numbers
            anns.append(annotation)
            ent_IDs.append(f'T{num_T}')

        return (ent_IDs, num_T, anns)


    def get_between_verbs(self, relation, verbs, sentence_num):
        """
        Get the verbs that come between two entities in a relation.
        Returns a list of updated relations, and also updates the self.verbs attribute. 

        parameters:
            relation, list: [start_tok1, end_tok1, start_tok2, end_tok2, "TYPE", logit, softmax]
            verbs, list of tuple: [(verb, token_idx), ...]
            sentence_num, int: index of the sentence list within self.sentences

        returns:
            relation, list: 
                [start_tok1, end_tok1, start_tok2, end_tok2, "TYPE", logit, softmax, verb1_tok_idx, verb2_tok_idx...]
        """
        # Convert the within-sentence token index for relation verbs
        updated_verbs = []
        for verb in verbs:
            new_idx = sum(len(i) for i in self.sentences[:sentence_num]) + verb[1]
            updated_verbs.append((verb[0], new_idx))
        
        # Check for in between verbs 
        between_verbs = []
        if relation[1] < relation[3]:
            for verb in updated_verbs:
                if relation [1] < verb[1] < relation[3]:
                    verb = [i for i in verbs if verb[0] == i[0]][0] # Use per-sentence index for further processing
                    between_verbs.append(verb)

        elif relation[1] > relation[3]:
            for verb in updated_verbs:
                if relation [3] < verb[1] < relation[0]:
                    verb = [i for i in verbs if verb[0] == i[0]][0] # Use per-sentence index for further processing
                    between_verbs.append(verb)
        
        for verb in between_verbs:
            relation.append(verb[1])
            self.relation_verbs.append(verb[0])

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
        sent_num = 0
        num_T = 0
        num_R = 0
        anns = []
        for relation_list, sentence in zip(self.relations, self.sentences):
            
            # Check if the sentence has relations 
            if len(relation_list) != 0:

                # Get a string with the sentence
                sentence_str = " ".join(sentence) + " "
                
                # Get all verbs in a sentence
                verbs = Doc.get_verbs(sentence_str, nlp)
                
                # Go through relations in the sentence 
                for relation in relation_list:

                    # Check if verbs come between entities
                    relation = self.get_between_verbs(relation, verbs, sent_num)
                    
                    # Get the annotations 
                    ## Entities 
                    ent_IDs, num_T, anns = self.get_entity_anns(relation, num_T, 
                                            anns, sentence, sentence_str)

                    ## Text-bound relational verbs
                    num_T, anns = self.get_rel_verb_anns(relation, num_T, anns, 
                                            sentence, sentence_str)           

                    ## Non-text-bound relations
                    num_R += 1
                    annotation = [sentence_str, f'R{num_R}', relation[4], 
                            f'Arg1:{ent_IDs[0]}', f'Arg2:{ent_IDs[1]}']
                    anns.append(annotation)

                # Add sentence to annotated sentences attribute 
                self.annotated_sentences += sentence_str
            
            sent_num += 1

        
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
        # Go through sentences in order, add to list to write if that 
        # sentence has annotations -- keeps the sentences in the correct order
        all_sents = [" ".join(sent) + " " for sent in self.sentences]
        ann_sentences = set([ann[0] for ann in self.anns])
        sents_to_write = []
        for sent in all_sents:
            if sent in ann_sentences:
                sents_to_write.append(sent[:-1])

        # Make one string to write
        sents_to_write_str = '\n'.join(sents_to_write)

        with open(f'{self.out_loc}/{self.doc_key}_rel_sentences.txt', 'w') as myfile:
            myfile.write(sents_to_write_str)
