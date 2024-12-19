#!/usr/bin/python3
from models.basemodel import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid

class Candidate(BaseModel, Base):
    __tablename__ = "candidates"
    candidateId = Column(String(60), primary_key=True)
    portfolio_id = Column(String(60), ForeignKey("portfolios.portfolioId"), nullable=False)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    contact = Column(String(20), nullable=False)
    email = Column(String(128), nullable=False)
    bio = Column(String(1028), nullable=True)
    manifesto = Column(String(1028), nullable=True)
    photo_url = Column(String(128), nullable=True)  # Changed from __photo_url
    #one to one relationship
    portfolio = relationship("Portfolio", back_populates="candidate", uselist=False) 

    def __init__(self, first_name, last_name, contact, email, portfolio_id, photo_url=None, bio=None, manifesto=None) -> None:
        super().__init__()
        # photo should be a url_link
        self.photo_url = photo_url  # Changed from __photo_url
        self.portfolio_id = portfolio_id
        self.bio = bio
        self.manifesto = manifesto
        self.first_name = first_name
        self.last_name = last_name
        self.candidateId = str(uuid.uuid4())
        self.contact = contact
        self.email = email
