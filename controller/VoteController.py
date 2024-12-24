from flask import  redirect, url_for, render_template
from controller import AuthController

class VoteController:
    
    @classmethod
    def route_vote(cls, request, candidate_group=None):
        token = request.args.get("token")
        session_id = request.cookies.get("session_id")
        voter = AuthController.get_cached_voter(token)
        if not voter:
            return redirect(url_for("login", token=token))
        
        confirmationNumber = voter.get('voteConfirmationNumber')
        if voter.get('session_id') == session_id and confirmationNumber == "NULL": 
            return render_template("vote.html", voter=voter,
                                candidate_group=candidate_group, token=token)
        elif voter.get('session_id') == session_id and confirmationNumber != "NULL":
            return redirect(url_for("report", token=token))
        
        return redirect(url_for("login", token=token))
       
