from models import db
from werkzeug.security import generate_password_hash
from flask import redirect, url_for, flash
from models.sms_email import Send


class RegisterController:
    
    @classmethod
    def register(cls, request):
        """
        Registers a new voter by processing the registration form data.

        Parameters:
        - cls: The class containing this method, used to access class-level methods.
        - request (Flask request object): The HTTP request object containing the form data
        for the registration, including first name, last name, email, contact, and password.

        Returns:
        - Flask Response: A redirect response to the registration page with a success or error message.
        """
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
            send = Send(token=new_voter.token, first_name=new_voter.first_name, host=request.host)
            send.send_email(voter_email_address=new_voter.email)
            #send.send_sms(contact=new_voter.contact)
            return redirect(url_for('register'))
        flash('Registration failed. User Already Exist!', 'info')
        return redirect(url_for('register'))
       
