import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

from database import db
from services.model_service import ModelService
from services.snapshot_service import SnapshotService


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///helmet_monitor.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    upload_dir = Path(app.root_path) / "uploads"
    weights_path = os.environ.get("MODEL_WEIGHTS")
    snapshot_service = SnapshotService(ModelService(weights_path=weights_path), upload_dir)

    @app.route("/")
    def camera_page():
        return render_template("camera.html")

    @app.route("/dashboard")
    def dashboard_page():
        return render_template("dashboard.html")

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(upload_dir, filename)

    @app.route("/api/predict", methods=["POST"])
    def predict():
        payload = request.get_json(silent=True) or {}
        image_b64 = payload.get("image")
        site = payload.get("site", "Unknown")
        if not image_b64:
            return jsonify({"error": "image is required"}), 400

        snapshot = snapshot_service.process_snapshot(image_b64, site)
        return jsonify(snapshot)

    @app.route("/api/dashboard", methods=["GET"])
    def dashboard_data():
        return jsonify(snapshot_service.get_dashboard_stats())

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
