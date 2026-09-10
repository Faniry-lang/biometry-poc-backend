CREATE TABLE Clients (
    IdClient                 INT UNSIGNED NOT NULL AUTO_INCREMENT,
    Firstnames               VARCHAR(255) NULL,
    Lastname                 VARCHAR(255) NULL,
    Telephone                VARCHAR(55) NULL,
    Email                    VARCHAR(255) NULL,
    IdentityNumber           VARCHAR(50) NULL,
    IsEnabled                CHAR(1) NULL,
    Comments                 VARCHAR(255) NULL,
    DateTimeCreated          DATETIME NULL,
    DateTimeModified         DATETIME NULL,
    BankIdClient              VARCHAR(55) NULL,
    DateTimeActivationToggle DATETIME NULL,
    Fingerprint              BLOB NULL,

    PRIMARY KEY (IdClient),
    UNIQUE KEY uq_client_telephone (Telephone),
    UNIQUE KEY uq_client_email (Email)
);