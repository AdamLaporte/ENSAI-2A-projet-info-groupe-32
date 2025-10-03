from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.database import Base  # Base provient de database.py

class Qrcode(Base):
    __tablename__ = "qrcodes"

    id_qrcode = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    id_proprietaire = Column(String, nullable=False)
    date_creation = Column(DateTime, default=datetime.utcnow)
    type = Column(Boolean, default=True)   # True/False selon usage
    couleur = Column(String, nullable=True)
    logo = Column(String, nullable=True)

    def __repr__(self):
        return f"<Qrcode(id={self.id_qrcode}, url={self.url}, proprietaire={self.id_proprietaire})>"
