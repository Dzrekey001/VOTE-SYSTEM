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
        """
        email = request.form["email"]
        password = request.form["password"]
        token = request.args.get("token")
        
        
        if not email or not password or not token:
            return None  # Missing data
        
        # Check Cache
        voter = cls.get_cached_voter(token)
        if voter:
            if voter.get('email') == email and voter.get("token") == token and check_password_hash(voter.get('passwordhash'), password):
                # Sync with DB if voteConfirmationNumber is missing or NULL
                if not voter.get('voteConfirmationNumber') or voter['voteConfirmationNumber'] == "NULL":
                    voter['voteConfirmationNumber'] = db.get_confirmationNumber(voter.get('id')) or "NULL"
                    session.cache_voter(token, voter)
                
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
        return None  # Return None instead of False for consistency
    
    @classmethod
    def remove_cached_voter(cls, userToken):
        """
        Remove a cached voter by token.
        """
        session.remove(f'user<{userToken}>')
    
    @classmethod
    def load_all_voter_to_cache(cls):
        """
        Load all voters from the database into the cache.
        """
        voters = db.get_all_voters()
        for voter in voters:
            session.set_email(voter.token, voter.email)
    
    @classmethod
    def cache_voter(cls, token, voter_data, ttl=3600):
        """
        Cache a voter with a specified TTL (default: 1 hour).
        """
        session.set(f'user<{token}>', voter_data, ttl=ttl)
