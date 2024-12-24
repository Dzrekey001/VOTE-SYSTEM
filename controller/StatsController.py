from flask import  redirect, url_for, render_template
from controller import AuthController

class StatsController:
    
    @classmethod
    def get_stats(cls, request, candidate_data):
        """
        Retrieves and displays voting statistics for the candidates.

        Parameters:
        - cls: The class containing this method, used to access class-level methods.
        - request (Flask request object): The HTTP request object containing the token and session data.
        - candidate_data (dict): A dictionary containing the vote statistics for each candidate.

        Returns:
        - Flask Response: A rendered HTML template displaying the voting statistics or a redirect
        to the login page if the voter is not authenticated.
        """
        token = request.args.get("token")
        session_id = request.cookies.get("session_id")
    
        voter = AuthController.get_cached_voter(token)
        if not voter:
                return redirect(url_for("login", token=token))
            
        if candidate_data and voter.get('session_id') == session_id and voter.get('token') == token:
            return render_template("statistics.html", candidate_data=candidate_data, token=token)
        return render_template("login.html", token=token)
     
       
