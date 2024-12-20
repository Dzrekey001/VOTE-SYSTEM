#!/usr/bin/python3
import os
from dotenv import load_dotenv 
from sqlalchemy import create_engine, or_, desc, asc,func
from sqlalchemy.orm import joinedload, aliased
from models.vote import Vote
from models.voter import Voter
from models.basemodel import Base
from sqlalchemy.orm import sessionmaker, scoped_session
from models.candidate import Candidate
from models.portfolio import Portfolio
from models.vote import Vote
from models.voter import Voter
from collections import OrderedDict

load_dotenv()


class DBStorage():
    """Database Storage"""
    __engine = None
    __session = None

    def __init__(self):
        """Initializes the object"""
        user = os.getenv('DBUSER')
        passwd = os.getenv('VOTEPASSWD')
        host = os.getenv('HOST')
        database = os.getenv('DB')
        self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'
                                      .format(user, passwd, host, database))
        
    def reload(self):
        """reloads data from the database"""
        Base.metadata.create_all(self.__engine)
        sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sess_factory)
        self.__session = Session
    
    def db_session(self):
        return self.__session

    def save(self):
        """commit all changes of the current database session"""
        self.__session.commit()

    def get_voter(self, email, token):
        voter = self.__session.query(Voter).filter((Voter.email == email) & (Voter.token == token)).first()
        if voter:
            return voter
        return False
    
    def get_all_voters(self):
        return self.__session.query(Voter).all()
       

    def get_candidates(self):
        candidates_grouped = (
            self.__session.query(Candidate)
            .order_by(asc(Candidate.portfolio_id), desc(Candidate.candidateId))
            .all())
        grouped_candidates = {}
        
        for candidate in candidates_grouped:
            portfolio_name = candidate.portfolio.portfolioName
            
            if portfolio_name not in grouped_candidates:
                grouped_candidates[portfolio_name] = []

            grouped_candidates[portfolio_name].append(candidate)

        return grouped_candidates


    def get_portfolioId(self, candidateId):
        portId = self.__session.query(Candidate).filter(Candidate.candidateId == candidateId).first().portfolio_id
        return portId
    
    def vote_count(self):
        return self.__session.query(Vote).count()
    
    def get_confirmationNumber(self, voterId):
        number = self.__session.query(Vote).filter(Vote.voter_Id == voterId).first()
        if number:
            return number.voteConfirmationNumber
        else:
            return None

    def get_voted_for(self, voter_id):
        voted_for = self.__session.query(Vote).join(Candidate).\
            options(joinedload(Vote.candidate)).\
            filter(Vote.voter_Id == voter_id).\
            order_by(asc(Candidate.portfolio_id )).all()

        return voted_for


    def cast_vote(self, voter_id, candidate_id, portfolio_id,voteConfirmationNumber):
        """
            Returns voteConfirmationNumber if vote successful.
        """
        if voter_id and candidate_id and portfolio_id:
            new_vote = Vote(
                candidateId=candidate_id,
                voteConfirmationNumber=voteConfirmationNumber,
                portfolioId=portfolio_id,
                voterId=voter_id)    
            self.__session.add(new_vote)
            self.save()
            return voteConfirmationNumber
        return None
    
    def register_voter(self, first_name=None, last_name=None, email=None, pwdhash=None, contact=None):
        """
            returns None if voter exist, voter_id on success
        """
        if first_name and last_name and email and pwdhash and contact:
            new_voter = Voter(
                first_name=first_name,
                last_name=last_name,
                email=email,
                passwordhash=pwdhash,
                contact=contact
            )
            self.__session.add(new_voter)
            self.save()
            return new_voter
        else:
            raise TypeError("missing argument")
    
    
    def add_portfolio(self, pname):
        """
            Create portfolios to the database
        """
        porfolio_does_not_exist = not(self.__session.query(Portfolio).filter(
            Portfolio.portfolioName == pname).first())
        if porfolio_does_not_exist:
            portfolio_id = (100 + self.__session.query(Portfolio).count())
            new_portfolio = Portfolio(
                portfolioName=pname,
                portfolioId=portfolio_id)
            self.__session.add(new_portfolio)
            self.save()
            return portfolio_id
        return None
    
    def register_candidate(self, first_name, last_name, contact,
                           email, porfolio_name, photo_url=None, 
                           bio=None, manifesto=None):
        """
            Returns None if the portfolio or candidate exits, else create an new candidate
        """
        if not self.check_existance(email=email, contact=contact, type="Candidate"):
            porfolio_exist = (self.__session.query(Portfolio).filter(
                Portfolio.portfolioName == porfolio_name).first())
            portfolio_id = str(porfolio_exist.portfolioId)
            if porfolio_exist:
                new_candidate = Candidate(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    contact=contact,
                    photo_url=photo_url,
                    portfolio_id=portfolio_id,
                    bio=bio,
                    manifesto=manifesto)
                self.__session.add(new_candidate)
                self.save()
                return new_candidate.candidateId
            return None
        return None
    
    def check_existance(self, contact, email, type):
        # check if user exists in the database
        classes = {"Voter": Voter, "Candidate": Candidate}
        if type not in classes.keys():
            raise TypeError(f"Type: '{type}' does not exist")
        class_type = classes[type]
        voter_exist = self.__session.query(class_type).filter(
            or_(class_type.contact == contact, class_type.email == email)).first()
        if voter_exist:
            return True
        else:
            return False           
    
    def get_vote_percentage_by_portfolio(self):
        try:
            # Create a mapping between portfolio_id and portfolio_name
            portfolio_mapping = dict(
                self.__session.query(Portfolio.portfolioId, Portfolio.portfolioName)
                .order_by(Portfolio.portfolioId)
                .all()
            )

            # Initialize the result dictionary
            result_dict = OrderedDict()

            # Initialize variables for overall total votes and percentage
            overall_total_votes = 0

            # Process each portfolio separately
            for portfolio_id, portfolio_name in portfolio_mapping.items():
                # Create a subquery to get all candidates for the current portfolio
                subquery = self.__session.query(
                    Candidate.candidateId.label('candidate_id'),
                    func.concat(Candidate.first_name, ' ', Candidate.last_name).label('full_name')
                ).filter(Candidate.portfolio_id == portfolio_id).subquery()

                # Left join the subquery with the votes
                vote_percentage = self.__session.query(
                    subquery.c.full_name,
                    func.coalesce(func.count(Vote.voteId), 0).label('total_votes'),
                    func.round(func.coalesce(func.count(Vote.voteId), 0) * 100.0 /
                            func.sum(func.coalesce(func.count(Vote.voteId), 0)).over(), 2).label('percentage')
                ).\
                    outerjoin(Vote, subquery.c.candidate_id == Vote.candidate_Id).\
                    group_by(subquery.c.full_name).\
                    order_by(desc('percentage')).\
                    all()

                # Process the query results for the current portfolio
                result_dict[portfolio_name] = OrderedDict()
                local_portfolio_total_votes = 0  # Initialize variable for local total votes in the portfolio

                for row in vote_percentage:
                    full_name, total_votes, percentage = row
                    result_dict[portfolio_name][full_name] = {
                        'total_votes': total_votes,
                        'percentage': percentage
                    }
                    local_portfolio_total_votes += total_votes  # Update local total votes

                # Calculate the correct percentage for Portfolio Total
                candidate_percentages = [candidate_info['percentage'] for candidate_info in result_dict[portfolio_name].values() if isinstance(candidate_info, dict)]
                result_dict[portfolio_name]['Portfolio Total'] = {
                    'total_votes': local_portfolio_total_votes,
                }

        except Exception as e:
            print(f"Error in get_vote_percentage_by_portfolio: {e}")
            return OrderedDict()

        return result_dict


Db = DBStorage()
Db.reload()

Db.get_all_voters()