from flask import  redirect, url_for, render_template
from controller import AuthController
from models import db


class ReportController:
    
    @classmethod
    def get_report(cls, request):
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
       
