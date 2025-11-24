from datetime import datetime
from database import db


class Snapshot(db.Model):
    __tablename__ = "snapshots"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    result = db.Column(db.String(32), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    site = db.Column(db.String(120), default="Unknown", nullable=False)
    image_path = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "result": self.result,
            "confidence": self.confidence,
            "site": self.site,
            "image_path": self.image_path,
        }
