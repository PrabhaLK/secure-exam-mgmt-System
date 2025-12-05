import random
import re
import nltk
import numpy as np
from nltk.corpus import wordnet as wn

class ObjectiveTest:

    FALLBACK_DISTRACTORS = [
        "Resource Pool",
        "Control Plane",
        "Infrastructure Node",
        "Service Layer",
        "Compute Cluster",
        "Baseline Module"
    ]

    def __init__(self, filepath, noOfQues):
        
        self.summary = filepath
        self.noOfQues = noOfQues

    def get_trivial_sentences(self):
        sentences = nltk.sent_tokenize(self.summary)
        trivial_sentences = list()
        for sent in sentences:
            trivial = self.identify_trivial_sentences(sent)
            if trivial:
                trivial_sentences.append(trivial)
            else:
                continue
        return trivial_sentences

    def identify_trivial_sentences(self, sentence):
        tokens = nltk.word_tokenize(sentence)
        if len(tokens) < 4:
            return None

        tags = nltk.pos_tag(tokens)
        if not tags or tags[0][1] == "RB":
            return None
        
        noun_phrases = list()
        grammer = r"""
            CHUNK: {<NN>+<IN|DT>*<NN>+}
                {<NN>+<IN|DT>*<NNP>+}
                {<NNP>+<NNS>*}
            """
        chunker = nltk.RegexpParser(grammer)
        pos_tokens = tags
        tree = chunker.parse(pos_tokens)

        for subtree in tree.subtrees():
            if subtree.label() == "CHUNK":
                temp = ""
                for sub in subtree:
                    temp += sub[0]
                    temp += " "
                temp = temp.strip()
                noun_phrases.append(temp)
        
        replace_nouns = []
        for word, _ in tags:
            for phrase in noun_phrases:
                if phrase[0] == '\'':
                    break
                if word in phrase:
                    [replace_nouns.append(phrase_word) for phrase_word in phrase.split()[-2:]]
                    break
            if len(replace_nouns) == 0:
                replace_nouns.append(word)
            break
        
        if len(replace_nouns) == 0:
            return None
        
        val = 99
        for i in replace_nouns:
            if len(i) < val:
                val = len(i)
            else:
                continue
        
        trivial = {
            "Answer": " ".join(replace_nouns),
            "Key": val
        }

        if len(replace_nouns) == 1:
            trivial["Similar"] = self.answer_options(replace_nouns[0])
        else:
            trivial["Similar"] = []
        
        replace_phrase = " ".join(replace_nouns)
        blanks_phrase = ("__________" * len(replace_nouns)).strip()
        expression = re.compile(re.escape(replace_phrase), re.IGNORECASE)
        sentence = expression.sub(blanks_phrase, str(sentence), count=1)
        trivial["Question"] = sentence
        return trivial

    @staticmethod
    def answer_options(word):
        synsets = wn.synsets(word, pos="n")

        if len(synsets) == 0:
            return []
        else:
            synset = synsets[0]
        
        hypernym = synset.hypernyms()[0]
        hyponyms = hypernym.hyponyms()
        similar_words = []
        for hyponym in hyponyms:
            similar_word = hyponym.lemmas()[0].name().replace("_", " ")
            if similar_word != word:
                similar_words.append(similar_word)
            if len(similar_words) == 8:
                break
        return similar_words

    def generate_test(self):
        trivial_pair = self.get_trivial_sentences()
        desired = int(self.noOfQues)
        question_answer = [qa for qa in trivial_pair if qa["Key"] > desired]

        if not question_answer:
            question_answer = list(trivial_pair)

        if not question_answer:
            return []

        unique_questions = {}
        for qa in question_answer:
            q_text = qa.get("Question")
            if q_text and q_text not in unique_questions:
                unique_questions[q_text] = qa
        question_answer = list(unique_questions.values())

        available = len(question_answer)
        take = min(desired, available)
        if take == 0:
            return []

        indices = np.atleast_1d(np.random.choice(available, take, replace=False))

        rows = []
        for idx, selection in enumerate(indices, start=1):
            qa = question_answer[int(selection)]
            question_text = self._normalize_text(qa.get("Question", ""))
            answer_text = self._normalize_text(qa.get("Answer", ""))
            similar = qa.get("Similar", []) or []

            options, correct_label = self._build_options(answer_text, similar)
            row = {
                "qid": idx,
                "q": question_text,
                "a": options[0],
                "b": options[1],
                "c": options[2],
                "d": options[3],
                "ans": correct_label,
                "marks": 1
            }
            rows.append(row)

        return rows

    @staticmethod
    def _normalize_text(value):
        if not value:
            return ""
        cleaned = value.replace("\n", " ")
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    def _build_options(self, answer, similar):
        seen = {answer.lower()}
        distractors = []

        def try_add(candidate):
            normalized = self._normalize_text(candidate)
            if not normalized:
                return
            if normalized.lower() in seen:
                return
            distractors.append(normalized)
            seen.add(normalized.lower())

        for candidate in similar:
            try_add(candidate)
            if len(distractors) == 3:
                break

        if len(distractors) < 3:
            extra_sources = self._collect_additional_distractors(answer)
            for candidate in extra_sources:
                try_add(candidate)
                if len(distractors) == 3:
                    break

        if len(distractors) < 3 and len(answer.split()) > 1:
            tail_word = answer.split()[-1]
            for candidate in self.answer_options(tail_word):
                try_add(candidate)
                if len(distractors) == 3:
                    break

        if len(distractors) < 3:
            for fallback in self.FALLBACK_DISTRACTORS:
                try_add(fallback)
                if len(distractors) == 3:
                    break

        while len(distractors) < 3:
            placeholder = f"Option {len(distractors) + 1}"
            try_add(placeholder)

        options = distractors[:3] + [answer]
        random.shuffle(options)
        correct_index = options.index(answer)
        correct_label = chr(ord('a') + correct_index)
        return options, correct_label

    def _collect_additional_distractors(self, answer):
        candidates = []
        synsets = wn.synsets(answer)
        for syn in synsets:
            for lemma in syn.lemmas():
                candidates.append(lemma.name())
            for relation in syn.hypernyms() + syn.hyponyms() + syn.similar_tos():
                for lemma in relation.lemmas():
                    candidates.append(lemma.name())
        cleaned = [candidate.replace('_', ' ') for candidate in candidates if candidate.lower() != answer.lower()]
        return cleaned