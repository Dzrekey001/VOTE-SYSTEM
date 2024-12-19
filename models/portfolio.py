#!/usr/bin/python3
from models.basemodel import BaseModel, Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from uuid import uuid4


class Portfolio(BaseModel, Base):
    __tablename__ = "portfolios"
    portfolioId = Column(String(60), primary_key=True)
    portfolioName = Column(String(128), nullable=False)
    #one to one relationship
    candidate = relationship("Candidate", back_populates="portfolio", uselist=False)

    def __init__(self, portfolioName, portfolioId) -> None:
        super().__init__()
        self.portfolioName = portfolioName
        self.portfolioId = portfolioId #DBStorage.generate_id("Portfolio")