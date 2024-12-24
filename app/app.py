from flask import Flask,render_template, redirect, request, url_for, flash
from models import db
from controller import AuthController
from controller import VoteController
from controller import RecordVoteController
from controller import RegisterController
from controller import StatsController
from controller import ReportController

candidate_group = db.get_candidates()

app = Flask(__name__)
app.secret_key = "f8fd933c-af3b-4e77-b6b9-cdb5f2dd42d3"


@app.route("/login/", methods=["GET", "POST"])
def login():
    """
    Handles the login process for GET and POST requests.

    GET: 
        - Retrieves a token from the query parameters.
        - Attempts to fetch a cached voter associated with the token.
        - If a voter is found, removes the cached voter.
        - Renders the login page.

    POST: 
        - Authenticates the user using the provided credentials.
        - If authentication is successful, returns the authenticated user's response.
        - If authentication fails, flashes an error message and redirects to the login page, 
          preserving the token in the query parameters.

    Returns:
        - For GET requests: Renders the login.html template.
        - For POST requests: Redirects to the login page on failure or returns the authenticated user on success.
    """
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
    """
    Handles the routing logic for accessing the voting page.

    This function performs the following steps:
    1. Retrieves the token from the query parameters.
    2. Fetches the cached voter associated with the token.
    3. Retrieves the session ID from the user's cookies.
    4. Validates the voter and session ID:
       - If no voter is found, redirects to the login page with the token.
       - If the session ID matches the cached voter's session ID, redirects to the voting route.
       - If the session ID does not match, redirects to the login page with the token.

    Returns:
        - Redirect to the login page if the voter is not found or the session ID does not match.
        - Redirect to the voting route if the session ID is valid.
    """
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
    """
    Handles the voting route logic based on the request method.

    GET:
        - Routes the voter to the appropriate voting logic using the `VoteController`.
        - The logic is processed with the `request` object and a `candidate_group` parameter.

    POST or Other Methods:
        - Redirects the user to the login page, preserving the `token` in the query parameters.

    Returns:
        - For GET requests: Returns the response from `VoteController.route_vote`.
        - For other request methods: Redirects to the login page with the token.
    """
    if request.method == "GET":
        route_voter = VoteController.route_vote(request, candidate_group)
        return route_voter
    else:
        return redirect(url_for("login", token=request.args.get("token")))


@app.route("/report")
def report():
    """
    Handles the generation and retrieval of a voting report for the authenticated user.
    Delegates the report generation and retrieval logic to the `ReportController.get_report` method.
    
    Returns:
        - The response from `ReportController.get_report`
    """
    return ReportController.get_report(request)


@app.route("/recordvote", methods=["POST"])
def recordvote():
    """
    Handles the logic for recording a voter's vote.

    Steps:
    1. Retrieves the token from the query parameters.
    2. Retrieves the session ID from the user's cookies.
    3. Fetches the cached voter using the token.
    4. Validates the voter and session:
       - If the voter is not found, redirects to the login page with the token.
       - If the session ID matches the cached voter's session ID and the vote has not been recorded,
         records the vote and redirects to the report page.
       - If validation fails, redirects to the login page with the token.

    Returns:
        - Redirect to the report page if the vote is successfully recorded.
        - Redirect to the login page if validation fails.
    """
    token = request.args.get("token")
    session_id = request.cookies.get("session_id")
    voter = AuthController.get_cached_voter(token)
    
    if not voter:
        return redirect(url_for("login", token=token))
        
    confirmationNumber = voter.get('voteConfirmationNumber')
    
    if voter.get('session_id') == session_id and confirmationNumber == "NULL":
        RecordVoteController.record_vote(request=request, voter=voter)
        return redirect(url_for("report", token=token))
    return redirect(url_for("login", token=token))


@app.route("/logout", methods=["GET", "POST"])
def logout():
    """
    Handles the logout functionality.

    POST:
        - Retrieves the token from the query parameters and the session ID from cookies.
        - Fetches the cached voter using the token.
        - Validates the voter and session:
            - If the voter is not found, redirects to the login page with the token.
            - If the session ID matches and the token is valid, logs the user out by flashing a success message
              and redirects to the login page with the token.
            - If validation fails, redirects to the login page with the token.

    GET:
        - Renders the login page with the token.

    Returns:
        - For POST requests: Redirects to the login page after validation.
        - For GET requests: Renders the login page.
    """
    if request.method == "POST":
        token = request.args.get("token")
        session_id = request.cookies.get("session_id")
        
        voter = AuthController.get_cached_voter(token)
        
        if voter:
            AuthController.remove_cached_voter(token)         
        return redirect(url_for("login", token=token))
    
    return render_template("login.html", token)
      

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Handles the registration process for new users.

    POST:
        - Processes the registration form data submitted via a POST request.
        - Delegates the registration logic to the `RegisterController.register` method, 
          which handles user creation and any necessary validations.

    GET:
        - Renders the registration page for users to fill out the registration form.
    """
    if request.method == "POST":
        return RegisterController.register(request)
    return render_template("register.html")


@app.route("/statistics")
def statistic():
    """
    This function:
    1. Fetches the vote percentages for candidates, grouped by their respective portfolios.
    2. Passes the data to the StatsController for processing and statistical analysis.
    3. Returns the processed statistics as a response.

    Returns:
        - The response from StatsController.get_stats
          depending on the implementation and request type.
    """
    candidate_data = db.get_vote_percentage_by_portfolio()
    return StatsController.get_stats(request, candidate_data)
    

if __name__ == "__main__":
    app.run(debug=True)