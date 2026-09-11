CREATE TABLE "Clients" (
    "IdClient" INTEGER GENERATED ALWAYS AS IDENTITY NOT NULL,
    "Firstnames" VARCHAR(255),
    "Lastname" VARCHAR(255),
    "Telephone" VARCHAR(55),
    "Email" VARCHAR(255),
    "IdentityNumber" VARCHAR(50),
    "IsEnabled" CHAR(1),
    "Comments" VARCHAR(255),
    "DateTimeCreated" TIMESTAMP,
    "DateTimeModified" TIMESTAMP,
    "BankIdClient" VARCHAR(55),
    "DateTimeActivationToggle" TIMESTAMP,

    PRIMARY KEY ("IdClient"),

    CONSTRAINT "uq_client_telephone"
        UNIQUE ("Telephone"),

    CONSTRAINT "uq_client_email"
        UNIQUE ("Email")
);


CREATE TABLE "Fingerprints" (
    "IdFingerprint" INTEGER GENERATED ALWAYS AS IDENTITY NOT NULL,
    "IdClient" INTEGER NOT NULL,
    "FingerprintLabel" VARCHAR NOT NULL,
    "CipherText" BYTEA NOT NULL,
    "IV" TEXT NOT NULL,
    "Tag" TEXT NOT NULL,
    "CreatedAt" TIMESTAMP NOT NULL,
    "RevokedAt" TIMESTAMP,

    PRIMARY KEY ("IdFingerprint"),

    CONSTRAINT "fk_fingerprint_client"
        FOREIGN KEY ("IdClient")
        REFERENCES "Clients" ("IdClient")
        ON DELETE CASCADE
);