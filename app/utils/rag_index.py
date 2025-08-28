import os
from typing import List, Tuple, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import glob

class RAGIndex:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.category_docs: Dict[str, List[str]] = {}
        self.category_paths: Dict[str, List[str]] = {}
        self.vectorizers: Dict[str, TfidfVectorizer] = {}
        self.matrices: Dict[str, Any] = {}
        self._load_all()

    def _load_all(self):
        for cat in ["Billing", "Technical", "Security", "General"]:
            path = os.path.join(self.base_dir, cat)
            files = sorted(glob.glob(os.path.join(path, "*.md")))
            docs = []
            for fp in files:
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        docs.append(f.read())
                except Exception:
                    docs.append("")
            self.category_docs[cat] = docs
            self.category_paths[cat] = files
            vec = TfidfVectorizer(stop_words="english")
            if docs:
                mat = vec.fit_transform(docs)
            else:
                mat = None
            self.vectorizers[cat] = vec
            self.matrices[cat] = mat

    def query(self, category: str, text: str, k: int = 4) -> List[str]:
        docs = self.category_docs.get(category, [])
        mat = self.matrices.get(category)
        vec = self.vectorizers.get(category)
        if not docs or mat is None or vec is None:
            return []
        q = vec.transform([text])
        sims = cosine_similarity(q, mat).flatten()
        idxs = sims.argsort()[::-1][:k]
        return [docs[i] for i in idxs if sims[i] > 0]

    def refine_query(self, base: str, feedback: str) -> str:
        # Simple refinement: append salient words from feedback
        add = " ".join(feedback.split()[:25])
        return (base + " " + add).strip()
