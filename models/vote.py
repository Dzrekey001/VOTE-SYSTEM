from models.basemodel import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid

class Vote(BaseModel, Base):
    __tablename__ = "votes"
    voteId = Column(String(60), primary_key=True)
    voteConfirmationNumber = Column(String(60), nullable=False)
    candidate_Id = Column(String(60), ForeignKey("candidates.candidateId"), nullable=False)
    voter_Id = Column(String(60), ForeignKey("voters.voterId"), nullable=False)
    portfolio_Id = Column(String(60), ForeignKey("portfolios.portfolioId"), nullable=False)
    candidate = relationship("Candidate", backref="vote")

    def __init__(self, candidateId=None, voterId=None, voteConfirmationNumber=None, portfolioId=None) -> None:
        super().__init__()
        self.voteId = str(uuid.uuid4())
        self.candidate_Id = candidateId
        self.voter_Id = voterId
        self.portfolio_Id = portfolioId
        self.voteConfirmationNumber = voteConfirmationNumber