from sqlalchemy import Column, String, CHAR, DateTime, LargeBinary, Integer, ForeignKey
from database import db


class Client(db.Model):
    __tablename__ = "Clients"

    IdClient = Column(
        Integer,
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

    IdentityNumber = Column(
        String(50),
        nullable=True
    )

    IsEnabled = Column(
        CHAR(1),
        nullable=True
    )

    Comments = Column(
        String(255),
        nullable=True
    )

    DateTimeCreated = Column(
        DateTime,
        nullable=True
    )

    DateTimeModified = Column(
        DateTime,
        nullable=True
    )

    BankIdClient = Column(
        String(55),
        nullable=True
    )

    DateTimeActivationToggle = Column(
        DateTime,
        nullable=True
    )

    Fingerprints = db.relationship(
        "Fingerprint",
        back_populates="Client",
        cascade="all, delete-orphan"
    )


class Fingerprint(db.Model):
    __tablename__ = "Fingerprints"

    IdFingerprint = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False
    )

    IdClient = Column(
        Integer,
        ForeignKey(
            "Clients.IdClient",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    FingerprintLabel = Column(
        String,
        nullable=False
    )

    CipherText = Column(
        LargeBinary,
        nullable=False
    )

    IV = Column(
        String,
        nullable=False
    )

    Tag = Column(
        String,
        nullable=False
    )

    CreatedAt = Column(
        DateTime,
        nullable=False
    )

    RevokedAt = Column(
        DateTime,
        nullable=True
    )

    Client = db.relationship(
        "Client",
        back_populates="Fingerprints"
    )