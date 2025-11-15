from sqlalchemy import Column, Integer, Text, Float, ForeignKey
from app.database import Base

class AttackVector(Base):
    __tablename__ = 'attack_vectors'
    
    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey('scans.id'))
    source_vuln_id = Column(Integer, ForeignKey('vulnerabilities.id'))
    target_vuln_id = Column(Integer, ForeignKey('vulnerabilities.id'))
    description = Column(Text)
    confidence = Column(Float)