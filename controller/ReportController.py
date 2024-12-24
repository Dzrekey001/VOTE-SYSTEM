from flask import  redirect, url_for, render_template
from controller import AuthController
from models import db


class ReportController:
    
    @classmethod
    def get_report(cls, request):
        """
        Retrieves and displays the voter's report after voting.

        Parameters:
        - cls: The class containing this method, used to access class-level methods.
        - request (Flask request object): The HTTP request object containing the token and session data.

        Returns:
        - Flask Response: A rendered HTML template displaying the voter's voting report or a redirect
        to the login page if the voter is not authenticated or hasn't voted.
        """
        token = request.args.get("token")
        session_id = request.cookies.get("session_id")
        voter = AuthController.get_cached_voter(token)
        
        if not voter:
            return redirect(url_for("login", token=token))
        
        confirmationNumber = voter.get('voteConfirmationNumber')
        
        if voter.get('session_id') == session_id and confirmationNumber != 'NULL':
            vote_casted = db.get_voted_for(voter.get('id'))
            return render_template("report.html", votes=vote_casted, voteConfirmationNumber=confirmationNumber, token=token )
  
        return redirect(url_for("login", token=token))
       
