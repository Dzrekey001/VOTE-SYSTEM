from flask import Flask,render_template, redirect, request, url_for, flash, make_response
from werkzeug.security import generate_password_hash
from models.sms_email import Send
from models import db
from controller.AuthController import AuthController
from models import session


candidate_group = db.get_candidates()

app = Flask(__name__)
app.secret_key = '1223fdferrewredf'

@app.route("/login/", methods=["GET", "POST"])
def login():  
    if request.method == "GET":
        response = make_response(render_template("login.html"))
        response.set_cookie('session_id', '', expires=0)
        return response
    
    if request.method == "POST":
        response = AuthController.user_authenticated(request)
        if response:
            return response
        else:
            flash('Login failed. Check credentials or use your unique link.', 'info')
            return redirect(url_for("login", token=request.args.get("token")))      
    

@app.route("/votes", methods=["GET", "POST"])
def votes():
    cached_voter=AuthController.get_cached_voter(request.args.get("token"))
    if cached_voter and cached_voter.get('session_id') == request.cookies.get('session_id'):
        return redirect(url_for("vote_route", token=request.args.get("token")))
    else:
        return redirect(url_for("login", token=request.args.get("token")))


@app.route("/vote", methods=["GET"])
def vote_route():
    token = request.args.get("token")
    user_session_id = request.cookies.get('session_id')
    voter = AuthController.get_cached_voter(token)
    
    
    if not voter or voter.get('session_id') != user_session_id:
        return redirect(url_for("login", token=token))
    
    confirmationNumber = voter.get('voteConfirmationNumber')
    if confirmationNumber == "NULL":
        return render_template("vote.html", voter=voter, candidate_group=candidate_group, token=token)
    return redirect(url_for("report", token=token))


@app.route("/report")
def report():
    token=request.args.get("token")
    voter = AuthController.get_cached_voter(token)
    if voter.get('voteConfirmationNumber') != "NULL":
        vote_casted = db.get_voted_for(voter.get("id"))
        return render_template("report.html", votes=vote_casted, voteConfirmationNumber=voter.get('voteConfirmationNumber') )
    return redirect(url_for("login", token=token))

@app.route("/recordvote", methods=["POST"])
def recordvote():
    token = request.args.get("token")
    session_id = request.cookies.get("session_id")
    voter = AuthController.get_cached_voter(token)
    
    if not voter or session_id != voter.get('session_id'):
        return redirect(url_for("login", token=token))
    
    if voter.get('voteConfirmationNumber') == 'NULL':
        voter_choice = request.form
        voteConfirmationNumber = str(db.vote_count() + 20000)
        
        for candidateId in voter_choice:
            portId = db.get_portfolioId(candidateId=candidateId)
            db.cast_vote(voter_id=voter.get('id'), candidate_id=candidateId, 
                         portfolio_id=portId, 
                         voteConfirmationNumber=voteConfirmationNumber)
        
        voter['voteConfirmationNumber'] = voteConfirmationNumber
        session.cache_voter(voter.get('token'), voter)
    
    return redirect(url_for("report", token=voter.get('token')))

@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        token = request.args.get("token")
        session_id = request.cookies.get("session_id")
        voter = AuthController.get_cached_voter(token)
        if not voter or session_id != voter.get('session_id'):
            flash('Something Happened.Try logging in.', 'error')
            return redirect(url_for("login", token=token))
    
        session.remove(f'user<{token}>')
        flash('You have been logged out successfully.', 'success')
        return redirect(url_for("login", token=token))
    return render_template("login.html", token=token)


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
            send = Send(token=new_voter.token, first_name=new_voter.first_name)
            send.send_email(voter_email_address=new_voter.email)
            #send.send_sms(contact=new_voter.contact)
            return redirect(url_for('register'))
        flash('Registration failed. User Already Exist!', 'info')
        return redirect(url_for('register'))
    return render_template("register.html")


@app.route("/statistics")
def statistic():
    token = request.args.get("token")
    candidate_data = db.get_vote_percentage_by_portfolio()
    if candidate_data:
        return make_response(render_template("statistics.html", candidate_data=candidate_data, token=token))
    return redirect(url_for("login", token=token))

     


if __name__ == "__main__":
    app.run(debug=True)