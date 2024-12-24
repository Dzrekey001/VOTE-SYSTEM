from models import db
from controller import AuthController

class RecordVoteController:
    
    @classmethod
    def record_vote(cls, request=None, voter=None):
        voter_choice = request.form
        voteConfirmationNumber = str(db.vote_count() + 20000)
        for candidateId in voter_choice:
            portId = db.get_portfolioId(candidateId=candidateId)
            db.cast_vote(voter_id=voter.get('id'), candidate_id=candidateId, 
                         portfolio_id=portId, 
                         voteConfirmationNumber=voteConfirmationNumber)
        voter['voteConfirmationNumber'] = voteConfirmationNumber
        AuthController.cache_voter(voter.get('token'), voter)
       
