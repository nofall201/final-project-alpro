import hashlib
import random
from typing import Dict


class ModelService:
    """
    A lightweight placeholder for a helmet detection model.
    Replace the logic in `predict` with calls to a real model when available.
    """

    labels = ["helmet", "no_helmet", "uncertain"]

    def __init__(self, seed: int = 42):
        random.seed(seed)

    def predict(self, image_bytes: bytes) -> Dict[str, float]:
        # Deterministic pseudo-random scoring based on image content hash.
        digest = hashlib.sha1(image_bytes).digest()
        score = int.from_bytes(digest[:2], "big") / 65535

        if score > 0.7:
            label = "helmet"
            confidence = score
        elif score < 0.3:
            label = "no_helmet"
            confidence = 1 - score
        else:
            label = "uncertain"
            confidence = 0.5

        return {"label": label, "confidence": round(confidence, 3)}
