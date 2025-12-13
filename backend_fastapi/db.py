from sqlmodel import SQLModel, Session, create_engine, select
from models import Detection

engine = create_engine("sqlite:///detections.db")

def init_db():
    SQLModel.metadata.create_all(engine)

def save_detection(person, violation, screenshot):
    from datetime import datetime
    detection = Detection(
        timestamp=datetime.now(),
        person_count=person,
        violation_count=violation,
        screenshot_path=screenshot
    )
    with Session(engine) as session:
        session.add(detection)
        session.commit()

def get_latest_detection():
    with Session(engine) as session:
        statement = select(Detection).order_by(Detection.id.desc())
        return session.exec(statement).first()

def get_all_detections():
    with Session(engine) as session:
        statement = select(Detection).order_by(Detection.id.desc())
        return session.exec(statement).all()

def get_detections_by_date(start, end):
    with Session(engine) as session:
        statement = (
            select(Detection)
            .where(Detection.timestamp >= start)
            .where(Detection.timestamp <= end)
            .order_by(Detection.timestamp.desc())
        )
        return session.exec(statement).all()
