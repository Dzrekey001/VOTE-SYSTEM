#!/usr/bin/python3
from datetime import datetime
from sqlalchemy import Column,DateTime

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class BaseModel():
        """
        BaseModel:Defines the common attributes among
                other classes.
        Attribute:
                name(str):
                        defines the name of the user:
                user_user_or_admin(int):
                        1 for admin, 0 for a user
                id(str):
                        id of the user
        """
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow)

        def __init__(self) -> None:
                self.created_at = datetime.now()
                self.updated_at = datetime.now()

        def to_dictionary(self):
                dictionary = self.__dict__.items()
                return dictionary


      