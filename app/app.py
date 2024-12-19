from flask import Flask,render_template, session, redirect, request, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models.sms_email import Send
from models import db
from controller import AuthController

candidate_group = db.get_candidates()

app = Flask(__name__)
app.secret_key = "f8fd933c-af3b-4e77-b6b9-cdb5f2dd42d3"

@app.route("/votes", methods=["GET", "POST"])
def votes():
    if session.get("voter_id"):
        return redirect(url_for("vote_route", token=session.get("token")))
    else:
        return redirect(url_for("login", token=session.get('token')))


@app.route("/vote", methods=["GET"])
def vote_route():
    voter = db.get_voter(session.get("email"), session.get("token"))
    confirmationNumber = db.get_confirmationNumber(voterId=session.get("voter_id"))
    if request.method == "GET":
        if voter and confirmationNumber is None: 
            return render_template("vote.html", voter=voter,
                                candidate_group=candidate_group)
        elif voter and confirmationNumber:
            return redirect(url_for("report", token=session.get("token")))
        else:
            return redirect(url_for("login", token=session.get("token")))
    else:
        return redirect(url_for("login", token=session.get("token")))

@app.route("/report")
def report():
    confirmationNumber = db.get_confirmationNumber(voterId=session.get("voter_id"))
    if confirmationNumber:
        vote_casted = db.get_voted_for(session.get("voter_id"))
        return render_template("report.html", votes=vote_casted, voteConfirmationNumber=confirmationNumber )
    return redirect(url_for("login", token=session.get("token")))

@app.route("/recordvote", methods=["POST"])
def recordvote():
    confirmationNumber = db.get_confirmationNumber(voterId=session.get("voter_id"))
    voter = db.get_voter(session.get("email"), session.get("token"))
    if voter and confirmationNumber is None:
        voter_choice = request.form
        voteConfirmationNumber = str(db.vote_count() + 20000)
        for candidateId in voter_choice:
            portId = db.get_portfolioId(candidateId=candidateId)
            db.cast_vote(voter_id=session.get("voter_id"), candidate_id=candidateId, 
                         portfolio_id=portId, 
                         voteConfirmationNumber=voteConfirmationNumber)
        return redirect(url_for("report", token=session.get("token")))
    else:
        return redirect(url_for("login", token=session.get("token")))

@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        token = session.get("token")
        session.clear()
        flash('You have been logged out successfully.', 'success')
        return redirect(url_for("login", token=token))
    return render_template("login.html", token)



@app.route("/login/", methods=["GET", "POST"])
def login():  
    if request.method == "GET": 
        if session.get("voter_id"):
            session.pop("token")
            session.pop("voter_id")
            session.pop("email")
        token_from_get = request.args.get("token")
        session["token"] = token_from_get 
        return render_template("login.html")
    
    if request.method == "POST":
        email = request.form["email"]
        voter_passwd = request.form["password"]
        
        voter = db.get_voter(email=email,token=session.get("token"))

        if voter and check_password_hash(voter.passwordhash, voter_passwd):
            session["voter_id"] = voter.id
            session["email"] = voter.email
            return redirect(url_for("votes"))
        else:
            flash('Login failed. Check credentials or use your unique link.', 'info')
            token = session.get('token')
            return redirect(url_for("login", token=token))      
    

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
     candidate_data = db.get_vote_percentage_by_portfolio()
     if candidate_data:
         return render_template("statistics.html", candidate_data=candidate_data)
     


if __name__ == "__main__":
    app.run(debug=True)