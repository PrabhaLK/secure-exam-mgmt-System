import numpy as np
import nltk as nlp

class SubjectiveTest:

    def __init__(self, filepath, noOfQues):

        self.question_pattern = [
            "Explain in detail ",
            "Define ",
            "Write a short note on ",
            "What do you mean by "
        ]
        self.grammar = r"""
            CHUNK: {<NN>+<IN|DT>*<NN>+}
            {<NN>+<IN|DT>*<NNP>+}
            {<NNP>+<NNS>*}
        """
        self.summary = filepath
        self.noOfQues = noOfQues
    
    @staticmethod
    def word_tokenizer(sequence):
        word_tokens = list()
        for sent in nlp.sent_tokenize(sequence):
            for w in nlp.word_tokenize(sent):
                word_tokens.append(w)
        return word_tokens
    
    def generate_test(self):
        sentences = nlp.sent_tokenize(self.summary)
        cp = nlp.RegexpParser(self.grammar)
        question_answer_dict = dict()
        for sentence in sentences:
            tagged_words = nlp.pos_tag(nlp.word_tokenize(sentence))
            tree = cp.parse(tagged_words)
            for subtree in tree.subtrees():
                if subtree.label() == "CHUNK":
                    temp = ""
                    for sub in subtree:
                        temp += sub[0]
                        temp += " "
                    temp = temp.strip()
                    temp = temp.upper()
                    if temp not in question_answer_dict:
                        if len(nlp.word_tokenize(sentence)) > 20:
                            question_answer_dict[temp] = sentence
                    else:
                        question_answer_dict[temp] += sentence
        keyword_list = list(question_answer_dict.keys())
        if not keyword_list:
            return [], []

        question_answer = []
        pattern_count = len(self.question_pattern)
        for idx, key in enumerate(keyword_list):
            question = self.question_pattern[idx % pattern_count] + key + "."
            question_answer.append({"Question": question, "Answer": question_answer_dict[key]})

        available = len(question_answer)
        if available == 0:
            return [], []

        desired = int(self.noOfQues)
        take = min(desired, available)
        indices = np.atleast_1d(np.random.choice(available, take, replace=False))
        que = [question_answer[i]["Question"] for i in indices]
        ans = [question_answer[i]["Answer"] for i in indices]
        return que, ans