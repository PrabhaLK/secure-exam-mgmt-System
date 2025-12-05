import math
import numpy as np
import nltk as nlp
import re

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
            return []

        question_answer = []
        pattern_count = len(self.question_pattern)
        for idx, key in enumerate(keyword_list):
            question = self._normalize_text(self.question_pattern[idx % pattern_count] + key + ".")
            answer = self._normalize_text(question_answer_dict[key])
            estimated_marks = self._estimate_marks(answer)
            question_answer.append({
                "Question": question,
                "Answer": answer,
                "Marks": estimated_marks
            })

        available = len(question_answer)
        if available == 0:
            return []

        desired = int(self.noOfQues)
        take = min(desired, available)
        indices = np.atleast_1d(np.random.choice(available, take, replace=False))

        rows = []
        for row_number, selection in enumerate(indices, start=1):
            qa = question_answer[int(selection)]
            rows.append({
                "qid": row_number,
                "q": qa["Question"],
                "marks": qa["Marks"],
                "answer": qa["Answer"]
            })

        return rows

    @staticmethod
    def _normalize_text(text):
        if not text:
            return ""
        cleaned = re.sub(r"\s+", " ", str(text).replace("\n", " "))
        return cleaned.strip()

    @staticmethod
    def _estimate_marks(answer_text):
        word_count = len(answer_text.split())
        if word_count == 0:
            return 1
        base = math.ceil(word_count / 40)
        return max(1, min(base, 10))