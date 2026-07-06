import json
import re
import string
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)


class FAQChatbot:
    def __init__(self, faqs_path: str = None):
        if faqs_path is None:
            faqs_path = str(Path(__file__).parent / "faqs.json")
        with open(faqs_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.faqs = data["faqs"]
        self.questions = [faq["question"] for faq in self.faqs]
        self.stop_words = set(stopwords.words("english"))
        self.stemmer = PorterStemmer()
        self.vectorizer = TfidfVectorizer(
            tokenizer=self._tokenize,
            token_pattern=None,
            max_features=5000,
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.questions)

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        tokens = word_tokenize(text)
        tokens = [self.stemmer.stem(t) for t in tokens if t not in self.stop_words and t not in string.punctuation]
        return tokens

    def preprocess(self, text: str) -> str:
        tokens = self._tokenize(text)
        return " ".join(tokens)

    def get_response(self, user_query: str, threshold: float = 0.08) -> dict:
        processed = self.preprocess(user_query)
        if not processed.strip():
            return {
                "answer": "I didn't catch that. Could you please rephrase your question?",
                "confidence": 0.0,
                "matched_question": None,
            }
        query_vec = self.vectorizer.transform([processed])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        best_idx = similarities.argmax()
        best_score = similarities[best_idx]

        if best_score < threshold:
            return {
                "answer": "I'm sorry, I don't have an answer for that. Please try rephrasing or contact our support team.",
                "confidence": float(best_score),
                "matched_question": None,
            }

        return {
            "answer": self.faqs[best_idx]["answer"],
            "confidence": float(best_score),
            "matched_question": self.questions[best_idx],
        }
