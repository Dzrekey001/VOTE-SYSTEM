from models import db
from controller import AuthController

class RecordVoteController:
    
    @classmethod
    def record_vote(cls, request=None, voter=None):
        """
        Records a voter's choice and updates their vote confirmation number.

        Parameters:
        - cls: The class containing this method, used to access class-level methods.
        - request (Flask request object, optional): The HTTP request object containing
          the voter's choices in the form data. Defaults to None.
        - voter (dict): A dictionary containing the voter's data, including their unique
          ID and token. This data is updated with the generated vote confirmation number.

        Returns:
        - None: This method does not return any value. It modifies the voter's data and
          updates the database.
        """
        voter_choice = request.form
        voteConfirmationNumber = str(db.vote_count() + 20000)
        for candidateId in voter_choice:
            portId = db.get_portfolioId(candidateId=candidateId)
            db.cast_vote(voter_id=voter.get('id'), candidate_id=candidateId, 
                         portfolio_id=portId, 
                         voteConfirmationNumber=voteConfirmationNumber)
        voter['voteConfirmationNumber'] = voteConfirmationNumber
        AuthController.cache_voter(voter.get('token'), voter)
       
