from flask import  redirect, url_for, render_template
from controller import AuthController

class VoteController:
    
    @classmethod
    def route_vote(cls, request, candidate_group=None):
        """
        Routes the voter to the appropriate voting page based on their authentication status
        and whether they have already voted.

        Parameters:
        - cls: The class containing this method, used to access class-level methods.
        - request (Flask request object): The HTTP request object containing the token and session data.
        - candidate_group (optional): A group of candidates to be displayed on the voting page.

        Returns:
        - Flask Response: A rendered HTML template for the voting page or the report page,
        or a redirect to the login page if the voter is not authenticated or the session is invalid.
        """
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
       
