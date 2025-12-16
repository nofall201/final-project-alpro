import hashlib
import io
import logging
import random
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ModelService:
    """
    Supports running a real .pth model when provided, with a deterministic stub fallback.

    Provide a weights path (e.g., env MODEL_WEIGHTS) to load your pretrained model.
    If loading fails or no path is given, we fall back to the stub so the app keeps working.
    """

    labels = ["helmet", "no_helmet", "uncertain"]

    def __init__(self, weights_path: Optional[str] = None, seed: int = 42, device: str = "cpu"):
        random.seed(seed)
        self.device = device
        self.model = None
        self.weights_path = Path(weights_path) if weights_path else None

        if self.weights_path:
            self._load_model()

    def _load_model(self):
        try:
            import torch

            self.model = torch.load(self.weights_path, map_location=self.device)
            self.model.eval()
            logger.info("Loaded model weights from %s", self.weights_path)
        except ImportError:
            logger.warning("torch not installed; using stub predictions instead")
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to load model %s (%s); using stub predictions", self.weights_path, exc)
            self.model = None

    def predict(self, image_bytes: bytes) -> Dict[str, float]:
        if self.model:
            return self._predict_with_model(image_bytes)
        return self._predict_stub(image_bytes)

    def _predict_with_model(self, image_bytes: bytes) -> Dict[str, float]:
        """
        Basic inference flow. Adjust preprocessing/postprocessing to match your model.
        """
        try:
            import torch
            from PIL import Image

            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            tensor = torch.as_tensor(list(image.getdata()), dtype=torch.float32).view(
                image.height, image.width, 3
            )
            # Normalize to [0,1] and add batch/channel dims.
            tensor = tensor.permute(2, 0, 1).unsqueeze(0) / 255.0

            with torch.no_grad():
                outputs = self.model(tensor)

            # Expecting model to return class scores; adapt mapping as needed.
            if isinstance(outputs, (list, tuple)):
                outputs = outputs[0]
            probs = torch.softmax(outputs, dim=-1).squeeze()
            confidence, idx = torch.max(probs, dim=-1)
            label = self.labels[idx.item()] if idx.item() < len(self.labels) else "uncertain"
            return {"label": label, "confidence": round(confidence.item(), 3)}
        except Exception as exc:  # pragma: no cover - defensive fallback
            logger.warning("Model inference failed (%s); using stub prediction", exc)
            return self._predict_stub(image_bytes)

    def _predict_stub(self, image_bytes: bytes) -> Dict[str, float]:
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
