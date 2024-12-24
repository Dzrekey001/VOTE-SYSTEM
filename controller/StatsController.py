from flask import  redirect, url_for, render_template
from controller import AuthController

class StatsController:
    
    @classmethod
    def get_stats(cls, request, candidate_data):
        token = request.args.get("token")
        session_id = request.cookies.get("session_id")
    
        voter = AuthController.get_cached_voter(token)
        if not voter:
                return redirect(url_for("login", token=token))
            
        if candidate_data and voter.get('session_id') == session_id and voter.get('token') == token:
            return render_template("statistics.html", candidate_data=candidate_data, token=token)
        return render_template("login.html", token=token)
     
       
