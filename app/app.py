from flask import Flask,render_template, redirect, request, url_for, flash
from werkzeug.security import generate_password_hash
from models.sms_email import Send
from models import db
from controller import AuthController

candidate_group = db.get_candidates()

app = Flask(__name__)
app.secret_key = "f8fd933c-af3b-4e77-b6b9-cdb5f2dd42d3"


@app.route("/login/", methods=["GET", "POST"])
def login():  
    if request.method == "GET": 
        token = request.args.get("token")
        voter = AuthController.get_cached_voter(token)
        if voter:
            AuthController.remove_cached_voter(token)
        return render_template("login.html")
    
    if request.method == "POST": 
        user_authenticed = AuthController.user_authenticated(request)

        if user_authenticed:
            return user_authenticed
        else:
            flash('Login failed. Check credentials or use your unique link.', 'info')
            token = request.args.get("token")
            return redirect(url_for("login", token=token))   
        
        
@app.route("/votes", methods=["GET", "POST"])
def votes():
    token = request.args.get("token")
    voter = AuthController.get_cached_voter(token)
    session_id = request.cookies.get("session_id")
    
    if not voter:
            return redirect(url_for("login", token=token))
        
    if session_id == voter.get("session_id"):
        return redirect(url_for("vote_route", token=token))
    else:
        return redirect(url_for("login", token=token))


@app.route("/vote", methods=["GET"])
def vote_route():
    if request.method == "GET":
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
    else:
        return redirect(url_for("login", token=token))


@app.route("/report")
def report():
    token = request.args.get("token")
    session_id = request.cookies.get("session_id")
    voter = AuthController.get_cached_voter(token)
    if not voter:
            return redirect(url_for("login", token=token))
        
    confirmationNumber = voter.get('voteConfirmationNumber')
    print(voter)
    
    if voter.get('session_id') == session_id and confirmationNumber != 'NULL':
        vote_casted = db.get_voted_for(voter.get('id'))
        return render_template("report.html", votes=vote_casted, voteConfirmationNumber=confirmationNumber, token=token )
  
    return redirect(url_for("login", token=token))


@app.route("/recordvote", methods=["POST"])
def recordvote():
    token = request.args.get("token")
    session_id = request.cookies.get("session_id")
    voter = AuthController.get_cached_voter(token)
    
    if not voter:
        return redirect(url_for("login", token=token))
        
    confirmationNumber = voter.get('voteConfirmationNumber')
  
    if voter.get('session_id') == session_id and confirmationNumber == "NULL":
        voter_choice = request.form
        voteConfirmationNumber = str(db.vote_count() + 20000)
        for candidateId in voter_choice:
            portId = db.get_portfolioId(candidateId=candidateId)
            db.cast_vote(voter_id=voter.get('id'), candidate_id=candidateId, 
                         portfolio_id=portId, 
                         voteConfirmationNumber=voteConfirmationNumber)
        return redirect(url_for("report", token=token))
    
    return redirect(url_for("login", token=token))

@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        token = request.args.get("token")
        session_id = request.cookies.get("session_id")
        
        voter = AuthController.get_cached_voter(token)
        
        if not voter:
            return redirect(url_for("login", token=token))
        
        if voter.get('session_id') == session_id and voter.get('token') == token:  
            flash('You have been logged out successfully.', 'success')
            return redirect(url_for("login", token=token))
        return redirect(url_for("login", token=token))
    return render_template("login.html", token)
   
    

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        contact = request.form["contact"]
        passwd = generate_password_hash(request.form["password"])
        
        if (db.check_existance(contact=contact, email=email, type="Voter") == False):
            new_voter = db.register_voter(first_name=first_name,
                                          last_name=last_name,
                                          email=email,
                                          pwdhash=passwd,
                                          contact=contact)           
            flash('Succesfully Register! Go to login', 'success')
            #send = Send(token=new_voter.token, first_name=new_voter.first_name)
            #send.send_email(voter_email_address=new_voter.email)
            #send.send_sms(contact=new_voter.contact)
            return redirect(url_for('register'))
        flash('Registration failed. User Already Exist!', 'info')
        return redirect(url_for('register'))
    return render_template("register.html")


@app.route("/statistics")
def statistic():
    token = request.args.get("token")
    session_id = request.cookies.get("session_id")
    candidate_data = db.get_vote_percentage_by_portfolio()
    
    voter = AuthController.get_cached_voter(token)
    if not voter:
            return redirect(url_for("login", token=token))
    
    if candidate_data and voter.get('session_id') == session_id and voter.get('token') == token:
        return render_template("statistics.html", candidate_data=candidate_data, token=token)
    return render_template("login.html", token=token)
     


if __name__ == "__main__":
    app.run(debug=True)