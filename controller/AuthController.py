from models import db
from models import session
from werkzeug.security import check_password_hash
from flask import make_response, redirect, url_for
import secrets

class AuthController:
    
    @classmethod  
    def user_authenticated(cls, request):
        """
        Authenticate a user based on email, password, and token.

        This function first checks the cache for voter data to optimize performance.
        If no valid cached voter is found, it queries the database as a fallback.
        Upon successful authentication, it sets a secure session cookie and redirects
        the user to the 'votes' route.

        Parameters:
        - cls: The class containing this method, used to access class-level methods
            like get_cached_voter and cache_voter.
        - request: The Flask request object containing user credentials (email, password)
                and a token in the query parameters.

        Returns:
        - Flask Response: A redirect response to the 'votes' route if authentication succeeds.
        - None: If authentication fails due to missing or invalid credentials.
        """
        email = request.form["email"]
        password = request.form["password"]
        token = request.args.get("token")
        
        if not email or not password or not token:
            return None
        
        # Check Cache
        voter = cls.get_cached_voter(token)
        if voter:
            if voter.get('email') == email and voter.get("token") == token and check_password_hash(voter.get('passwordhash'), password):
                if not voter.get('voteConfirmationNumber') or voter['voteConfirmationNumber'] == "NULL":
                    voter['voteConfirmationNumber'] = db.get_confirmationNumber(voter.get('id')) or "NULL"
                    cls.cache_voter(token, voter)
                response = make_response(redirect(url_for("votes", token=token)))
                response.set_cookie('session_id', voter.get('session_id'), httponly=True, secure=True, samesite='Strict')
                return response
        
        # Fallback to Database
        voter = db.get_voter(email=email, token=token)
        if voter and voter.email == email and voter.token == token and check_password_hash(voter.passwordhash, password):
            session_id = secrets.token_hex(32)
            voteConfirm = db.get_confirmationNumber(voter.id) or "NULL"
            
            user_cache = {
                **voter.to_dictionary(),
                'session_id': session_id,
                'user_ip': request.remote_addr,
                'voteConfirmationNumber': voteConfirm,
            }
            session.cache_voter(token, user_cache)
            
            response = make_response(redirect(url_for("votes", token=token)))
            response.set_cookie('session_id', session_id, httponly=True, secure=True, samesite='Strict')
            return response
        
        return None


    @classmethod
    def get_cached_voter(cls, token):
        """
        Retrieve a cached voter by token and refresh TTL if necessary.
        """
        cached_user = session.get_cached_voter(token)
        if cached_user:
            return cached_user
        return None  
    
    
    @classmethod
    def remove_cached_voter(cls, userToken):
        """
        Remove a cached voter by token.
        """
        session.remove(f'user<{userToken}>')


    @classmethod
    def cache_voter(cls, token, voter_data, ttl=3600):
        """
        Cache voter data associated with a specific token.
        
        Parameters:
        - token (str): The unique token identifying the voter.
        - voter_data (dict): A dictionary containing the voter's information to be cached.
        - ttl (int, optional): Time-to-live for the cached data, in seconds. Defaults to 3600 seconds (1 hour).

        Returns:
        - None
        """
        session.remove(token)
        session.cache_voter(token, voter_data, ttl=ttl)

