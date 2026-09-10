from sqlalchemy import Column, String, CHAR, DateTime, LargeBinary
from sqlalchemy.dialects.mysql import INTEGER
from database import db

class Client(db.Model):
    __tablename__ = "Clients"

    IdClient = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )

    Firstnames = Column(String(255), nullable=True)
    Lastname = Column(String(255), nullable=True)

    Telephone = Column(
        String(55),
        unique=True,
        nullable=True
    )

    Email = Column(
        String(255),
        unique=True,
        nullable=True
    )

    IdentityNumber = Column(String(50), nullable=True)
    IsEnabled = Column(CHAR(1), nullable=True)
    Comments = Column(String(255), nullable=True)

    DateTimeCreated = Column(DateTime, nullable=True)
    DateTimeModified = Column(DateTime, nullable=True)

    BankIdClient = Column(String(55), nullable=True)

    DateTimeActivationToggle = Column(DateTime, nullable=True)
    Fingerprint = Column(LargeBinary, nullable=True)