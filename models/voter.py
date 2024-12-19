#!/usr/bin/python3
from models.basemodel import BaseModel, Base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
import shortuuid
import uuid

class Voter(BaseModel, Base):
    __tablename__ = "voters"
    id = Column('voterId', String(60), primary_key=True)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    contact = Column(String(20), nullable=False)
    email = Column(String(128), nullable=False)
    token = Column("token",String(50), nullable=False)
    passwordhash = Column("passwordhash", String(1024), nullable=False)
    __user_type = Column("userType", Integer, nullable=False)

    def __init__(self, first_name,last_name, email, passwordhash, contact) -> None:
        super().__init__()
        #implement a feature to check if generated token does not already exist
        #token to be added to link
        self.token = str(shortuuid.uuid())
        self.__user_type = 0
        self.passwordhash = passwordhash
        self.first_name =  first_name
        self.last_name =  last_name
        self.id = str(uuid.uuid4())
        self.contact = contact
        self.email = email
